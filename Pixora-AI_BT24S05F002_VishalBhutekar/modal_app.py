"""Modal GPU inference app for Pixora Real-ESRGAN."""

from __future__ import annotations

import io
import os
from pathlib import Path
import sys
import types

import modal

APP_NAME = "pixora-ai-enhance"
VOLUME_NAME = "pixora-models"
CONTAINER_WEB_DIST = Path("/web-dist")

_module_path = Path(__file__).resolve()
_local_web_dist: Path | None = None
if len(_module_path.parents) >= 3:
    candidate = _module_path.parents[2] / "web" / "dist"
    if candidate.exists():
        _local_web_dist = candidate

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "libgl1", "libglib2.0-0")
    .pip_install(
        "numpy>=1.26.0,<3",
        "pillow>=10.4.0,<11",
        "torch>=2.4.0,<3",
        "torchvision>=0.19.0,<1",
        "opencv-python-headless>=4.10.0,<5",
        "fastapi[standard]>=0.115.0,<1",
        "python-multipart>=0.0.9,<1",
        "lmdb>=1.4.1,<2",
        "pyyaml>=6.0,<7",
        "scipy>=1.11.0,<2",
        "future>=1.0.0,<2",
        "yapf>=0.40.0,<1",
    )
    .run_commands(
        "git clone --depth 1 --branch v1.4.2 https://github.com/XPixelGroup/BasicSR.git /tmp/BasicSR",
        "python -m pip install --no-build-isolation /tmp/BasicSR",
        "python -m pip install 'realesrgan>=0.3.0,<1'",
    )
)

if _local_web_dist is not None:
    image = image.add_local_dir(
        local_path=str(_local_web_dist),
        remote_path="/web-dist",
        copy=True,
    )

app = modal.App(APP_NAME, image=image)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


@app.cls(gpu="A10G", volumes={"/models": volume}, scaledown_window=300)
class InferenceService:
    @modal.enter()
    def load(self):
        print("[modal] Starting InferenceService load...")
        volume.reload()
        # BasicSR/Real-ESRGAN may import a removed torchvision module path on
        # newer torchvision versions. Add a tiny runtime shim for compatibility.
        try:
            import torchvision.transforms.functional_tensor  # type: ignore # noqa: F401
        except Exception:
            try:
                from torchvision.transforms import functional as functional_mod

                shim = types.ModuleType("torchvision.transforms.functional_tensor")
                if hasattr(functional_mod, "rgb_to_grayscale"):
                    shim.rgb_to_grayscale = functional_mod.rgb_to_grayscale
                sys.modules["torchvision.transforms.functional_tensor"] = shim
            except Exception:
                # Let downstream import error surface with original context.
                pass

        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer
        import torch

        self.weights_path = Path("/models/RealESRGAN_x2plus.pth")
        model_path = str(self.weights_path)
        if not os.path.exists(model_path):
            raise RuntimeError(
                "RealESRGAN model weights not uploaded to Modal volume. "
                f"Expected at {model_path}. "
                "Upload local weights before deploy."
            )
        print(f"[modal] GPU available: {torch.cuda.is_available()}")
        print(f"[modal] Weights loaded from: {model_path}")

        rrdb = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=2,
        )
        self.model = RealESRGANer(
            scale=2,
            model_path=model_path,
            model=rrdb,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=True,
            gpu_id=0,
        )
        print("[modal] RealESRGAN initialized.")
        print("[modal] Inference ready.")

    @modal.method()
    def enhance_bytes(self, image_bytes: bytes, strength: float, output_format: str) -> bytes:
        import numpy as np
        from PIL import Image

        src = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        src_np = np.array(src)[:, :, ::-1]
        out_bgr, _ = self.model.enhance(src_np, outscale=2)
        enhanced = Image.fromarray(out_bgr[:, :, ::-1])
        if src.size != enhanced.size:
            src = src.resize(enhanced.size, Image.Resampling.LANCZOS)
        blended = Image.blend(src, enhanced, alpha=max(0, min(1, strength)))
        buffer = io.BytesIO()
        fmt = "JPEG" if output_format.lower() in {"jpeg", "jpg"} else "PNG"
        kwargs = {"quality": 92, "optimize": True} if fmt == "JPEG" else {}
        blended.save(buffer, format=fmt, **kwargs)
        return buffer.getvalue()


@app.function()
@modal.asgi_app()
def web_app():
    # Use pure Starlette (no FastAPI) to avoid Pydantic parameter validation in
    # Modal's runtime, which misidentifies `Request` as a query parameter.
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import FileResponse, JSONResponse, Response
    from starlette.routing import Route

    dist_root = CONTAINER_WEB_DIST

    async def health(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok", "service": "pixora-modal"})

    async def enhance(request: Request) -> Response:
        # Raw binary body + query params — no multipart parsing needed
        content = await request.body()

        try:
            strength = float(request.query_params.get("strength", "0.7"))
        except (TypeError, ValueError):
            return JSONResponse({"error": "Invalid strength value."}, status_code=400)

        fmt = str(request.query_params.get("output_format", "jpeg")).lower()

        if not content:
            return JSONResponse({"error": "Empty image payload."}, status_code=400)
        if not 0.0 <= strength <= 1.0:
            return JSONResponse({"error": "strength must be in [0, 1]."}, status_code=400)
        if fmt not in {"jpeg", "jpg", "png"}:
            return JSONResponse({"error": "output_format must be jpeg or png."}, status_code=400)

        service = InferenceService()
        try:
            enhanced = await service.enhance_bytes.remote.aio(content, strength, fmt)
        except Exception as exc:
            return JSONResponse({"error": f"Inference error: {exc}"}, status_code=500)

        media_type = "image/jpeg" if fmt in {"jpg", "jpeg"} else "image/png"
        return Response(content=enhanced, media_type=media_type)

    async def spa_fallback(request: Request) -> Response:
        """Serve index.html for any path that doesn't map to a static asset."""
        path = request.path_params.get("path", "")
        if path:
            candidate = dist_root / path
            if candidate.exists() and candidate.is_file():
                return FileResponse(str(candidate))
        index_file = dist_root / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse({"error": "Frontend bundle missing."}, status_code=500)

    return Starlette(
        routes=[
            Route("/health", health, methods=["GET"]),
            Route("/enhance", enhance, methods=["POST"]),
            Route("/{path:path}", spa_fallback, methods=["GET", "HEAD"]),
        ]
    )

