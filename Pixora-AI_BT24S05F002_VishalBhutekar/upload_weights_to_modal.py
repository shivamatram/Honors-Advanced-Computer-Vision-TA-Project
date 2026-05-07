"""Upload local RealESRGAN weights into Modal volume."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

VOLUME_NAME = "pixora-models"
LOCAL_WEIGHTS = Path(__file__).resolve().parents[1] / "models" / "RealESRGAN_x2plus.pth"
REMOTE_WEIGHTS = "/RealESRGAN_x2plus.pth"


def main() -> int:
    if not LOCAL_WEIGHTS.exists():
        print(f"[error] Local weights not found: {LOCAL_WEIGHTS}")
        print("[hint] Place the file at apps/api/models/RealESRGAN_x2plus.pth")
        return 1

    modal_bin = shutil.which("modal")
    cmd: list[str]
    if modal_bin:
        cmd = [modal_bin, "volume", "put", VOLUME_NAME, str(LOCAL_WEIGHTS), REMOTE_WEIGHTS]
    else:
        cmd = [
            sys.executable,
            "-m",
            "modal",
            "volume",
            "put",
            VOLUME_NAME,
            str(LOCAL_WEIGHTS),
            REMOTE_WEIGHTS,
        ]

    print(f"[upload] Uploading {LOCAL_WEIGHTS} -> {VOLUME_NAME}:{REMOTE_WEIGHTS}")
    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        print("[error] Failed to upload weights to Modal volume.")
        return completed.returncode

    print("[upload] Weights uploaded successfully.")
    print("[upload] You can verify with: modal volume ls pixora-models")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
