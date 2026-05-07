"""
Motion Detection & Object Tracking
===================================
Handles fast-moving objects by combining:
  1. CSRT tracker (accurate appearance model)
  2. Kalman filter  (velocity-based position prediction)
  3. Lucas-Kanade sparse optical flow (fast-motion displacement estimation)

When CSRT loses the object, the Kalman-predicted position (adjusted by OF
displacement) is used to instantly re-seed a fresh CSRT tracker.
"""

import cv2
import numpy as np
from collections import deque
import time

# ────────────────────────── CONFIG ──────────────────────────────
WINDOW_NAME      = "Motion Detection & Object Tracking"
FRAME_WIDTH      = 800
FRAME_HEIGHT     = 500

MOTION_THRESHOLD = 0.008          # fraction of changed pixels → motion
SMOOTH_WINDOW    = 5              # frames for majority-vote smoothing
ALPHA_REF        = 0.05           # reference frame learning rate
BOX_SMOOTH       = 0.55           # EMA factor for display box (0=frozen, 1=raw)

MAX_REINIT       = 10             # max consecutive auto re-init attempts
REINIT_COOLDOWN  = 0.10           # seconds between re-init attempts
VELOCITY_SCALE   = 1.8            # how far ahead of velocity to search
SEARCH_EXPAND    = 1.4            # expand re-init box by this factor

LK_PARAMS = dict(
    winSize  = (21, 21),
    maxLevel = 3,
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01),
)
FEATURE_PARAMS = dict(
    maxCorners   = 80,
    qualityLevel = 0.2,
    minDistance  = 5,
    blockSize    = 5,
)
# ────────────────────────────────────────────────────────────────


# ══════════════ Kalman filter for (cx, cy, w, h) + velocity ════
class KalmanBoxTracker:
    """Constant-velocity Kalman filter over [cx, cy, w, h, vx, vy, vw, vh]."""

    def __init__(self, box):
        self.kf = cv2.KalmanFilter(8, 4)

        # Transition: x_k+1 = x_k + v_k
        T = np.eye(8, dtype=np.float32)
        T[0, 4] = T[1, 5] = T[2, 6] = T[3, 7] = 1.0
        self.kf.transitionMatrix = T

        # Measurement: observe (cx, cy, w, h)
        H = np.zeros((4, 8), dtype=np.float32)
        H[0, 0] = H[1, 1] = H[2, 2] = H[3, 3] = 1.0
        self.kf.measurementMatrix = H

        # Noise covariances
        self.kf.processNoiseCov     = np.eye(8, dtype=np.float32) * 1e-2
        self.kf.processNoiseCov[4:, 4:] *= 80   # allow fast velocity changes
        self.kf.measurementNoiseCov = np.eye(4, dtype=np.float32) * 4.0
        self.kf.errorCovPost        = np.eye(8, dtype=np.float32) * 50

        cx, cy, w, h = self._xywh_to_center(box)
        self.kf.statePost = np.array(
            [cx, cy, w, h, 0, 0, 0, 0], dtype=np.float32
        ).reshape(8, 1)

    @staticmethod
    def _xywh_to_center(box):
        x, y, w, h = box
        return x + w / 2, y + h / 2, float(w), float(h)

    @staticmethod
    def _center_to_xywh(cx, cy, w, h):
        return int(cx - w / 2), int(cy - h / 2), max(4, int(w)), max(4, int(h))

    def velocity(self):
        """Return (vx, vy) in pixels/frame."""
        s = self.kf.statePost.flatten()
        return float(s[4]), float(s[5])

    def predict(self):
        """Predict next-frame box (x, y, w, h)."""
        p = self.kf.predict()
        return self._center_to_xywh(p[0, 0], p[1, 0], p[2, 0], p[3, 0])

    def update(self, box):
        """Correct filter with observed box (x, y, w, h)."""
        cx, cy, w, h = self._xywh_to_center(box)
        z = np.array([cx, cy, w, h], dtype=np.float32).reshape(4, 1)
        self.kf.correct(z)


# ══════════════════════════ Helpers ═════════════════════════════
def clamp_box(x, y, w, h):
    x = max(0, min(x, FRAME_WIDTH  - 4))
    y = max(0, min(y, FRAME_HEIGHT - 4))
    w = max(4, min(w, FRAME_WIDTH  - x))
    h = max(4, min(h, FRAME_HEIGHT - y))
    return x, y, w, h


def make_tracker():
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    if hasattr(cv2, "TrackerKCF_create"):
        print("[WARN] CSRT unavailable, using KCF.")
        return cv2.TrackerKCF_create()
    raise RuntimeError("No tracker found. Install opencv-contrib-python.")


def init_tracker(frame, box):
    """Return new tracker initialised on `box`, or None on failure."""
    t = make_tracker()
    b = (int(box[0]), int(box[1]), int(box[2]), int(box[3]))
    result = t.init(frame, b)
    return t if result is not False else None


def detect_features(gray, box):
    """Detect Shi-Tomasi corners inside the bounding box."""
    x, y, w, h = box
    mask = np.zeros_like(gray)
    mask[y:y + h, x:x + w] = 255
    pts = cv2.goodFeaturesToTrack(gray, mask=mask, **FEATURE_PARAMS)
    return pts   # shape (N,1,2) or None


def optical_flow_displacement(prev_gray, cur_gray, pts):
    """
    Track `pts` from prev_gray → cur_gray with LK.
    Returns median (dx, dy) displacement.
    """
    if pts is None or len(pts) == 0:
        return 0.0, 0.0
    new_pts, status, _ = cv2.calcOpticalFlowPyrLK(
        prev_gray, cur_gray, pts, None, **LK_PARAMS
    )
    if new_pts is None:
        return 0.0, 0.0
    good = (status.flatten() == 1)
    if good.sum() == 0:
        return 0.0, 0.0
    disp = (new_pts[good] - pts[good]).reshape(-1, 2)
    dx   = float(np.median(disp[:, 0]))
    dy   = float(np.median(disp[:, 1]))
    return dx, dy


def expand_box(box, factor):
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    nw, nh = w * factor, h * factor
    return clamp_box(int(cx - nw / 2), int(cy - nh / 2), int(nw), int(nh))


def smooth_ema(prev, cur, alpha):
    if prev is None:
        return cur
    return tuple(int(p + alpha * (c - p)) for p, c in zip(prev, cur))


# ══════════════════════════ HUD ═════════════════════════════════
def draw_overlay(frame, status, color, fps,
                 smooth_box, raw_box, motion_score, reinit_count, vel):
    H, W  = frame.shape[:2]

    # ── top bar
    bar = frame.copy()
    cv2.rectangle(bar, (0, 0), (W, 44), (18, 18, 18), -1)
    cv2.addWeighted(bar, 0.55, frame, 0.45, 0, frame)

    cv2.putText(frame, status, (12, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2, cv2.LINE_AA)

    fps_str = f"FPS: {fps:.1f}"
    (fw, _), _ = cv2.getTextSize(fps_str, cv2.FONT_HERSHEY_SIMPLEX, 0.60, 1)
    cv2.putText(frame, fps_str, (W - fw - 10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.60, (180, 180, 180), 1, cv2.LINE_AA)

    # velocity indicator
    if smooth_box is not None and (abs(vel[0]) + abs(vel[1])) > 0.5:
        spd = f"Speed: {(vel[0]**2+vel[1]**2)**0.5:.1f} px/f"
        cv2.putText(frame, spd, (12, H - 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 200, 255), 1, cv2.LINE_AA)

    if reinit_count > 0:
        ri = f"Re-init: {reinit_count}/{MAX_REINIT}"
        (rw, _), _ = cv2.getTextSize(ri, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)
        cv2.putText(frame, ri, (W - rw - 10, 46),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 180, 255), 1, cv2.LINE_AA)

    # ── raw box (faint)
    if raw_box is not None and smooth_box is not None:
        rx, ry, rw, rh = raw_box
        cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), (70, 70, 70), 1)

    # ── smoothed box + corners
    if smooth_box is not None:
        x, y, bw, bh = smooth_box
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)

        cl, ct = 16, 3
        for cx, cy_, dx, dy in [
            (x,      y,         1,  1),
            (x + bw, y,        -1,  1),
            (x,      y + bh,    1, -1),
            (x + bw, y + bh,   -1, -1),
        ]:
            cv2.line(frame, (cx, cy_), (cx + dx * cl, cy_),  color, ct)
            cv2.line(frame, (cx, cy_), (cx, cy_ + dy * cl),  color, ct)

        # Velocity arrow (from box centre)
        if (abs(vel[0]) + abs(vel[1])) > 0.5:
            ox, oy = x + bw // 2, y + bh // 2
            ex = int(ox + vel[0] * 4)
            ey = int(oy + vel[1] * 4)
            cv2.arrowedLine(frame, (ox, oy), (ex, ey),
                            (0, 220, 255), 2, tipLength=0.35)

        # Motion bar
        by = min(y + bh + 6, H - 14)
        filled = int(bw * min(motion_score / max(MOTION_THRESHOLD * 5, 1e-6), 1.0))
        bc = (0, 220, 80) if motion_score < MOTION_THRESHOLD else (0, 60, 255)
        cv2.rectangle(frame, (x, by), (x + bw, by + 7), (50, 50, 50), -1)
        if filled > 0:
            cv2.rectangle(frame, (x, by), (x + filled, by + 7), bc, -1)

    # ── bottom hint
    hint_bar = frame.copy()
    cv2.rectangle(hint_bar, (0, H - 28), (W, H), (18, 18, 18), -1)
    cv2.addWeighted(hint_bar, 0.55, frame, 0.45, 0, frame)
    cv2.putText(frame, "  [S] Select object    [R] Reset    [Q] Quit",
                (8, H - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.48,
                (140, 140, 140), 1, cv2.LINE_AA)


# ══════════════════════════ MAIN ════════════════════════════════
def open_camera(index=0, retries=3):
    for attempt in range(retries):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            cap.set(cv2.CAP_PROP_FPS, 30)
            print(f"[INFO] Camera opened (attempt {attempt + 1}).")
            return cap
        cap.release()
        time.sleep(0.4)
    return None


def main():
    cap = open_camera(0)
    if cap is None:
        print("[ERROR] Could not open camera.")
        return

    # ── state variables
    tracker        = None
    kalman         = None
    last_good_box  = None     # last box where CSRT succeeded
    smooth_box     = None     # EMA-smoothed display box
    reference_f    = None     # float32 reference frame
    motion_history = deque(maxlen=SMOOTH_WINDOW)

    reinit_count   = 0
    last_reinit_t  = 0.0

    prev_gray  = None         # for optical flow
    of_pts     = None         # feature points to track

    prev_time  = time.time()
    fps        = 0.0
    vel        = (0.0, 0.0)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, FRAME_WIDTH, FRAME_HEIGHT)
    print("[INFO] Running — S: select  R: reset  Q: quit")

    while True:
        # ── grab & preprocess ─────────────────────────────────────
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame grab failed. Reconnecting…")
            cap.release()
            time.sleep(0.5)
            cap = open_camera(0)
            if cap is None:
                break
            continue

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

        gray_blur = cv2.GaussianBlur(
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0
        )
        gray_raw  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        now       = time.time()
        fps       = 0.9 * fps + 0.1 / max(now - prev_time, 1e-6)
        prev_time = now

        status      = "Press [S] to select an object"
        color       = (0, 200, 255)
        raw_box     = None
        motion_score = 0.0

        # ── tracker update ────────────────────────────────────────
        if tracker is not None:
            # ① Kalman prediction (tells us where to look if CSRT fails)
            kalman_pred = kalman.predict() if kalman else None

            # ② Optical flow displacement estimate
            of_dx, of_dy = 0.0, 0.0
            if prev_gray is not None and of_pts is not None:
                of_dx, of_dy = optical_flow_displacement(prev_gray, gray_raw, of_pts)

            # ③ CSRT update
            success, raw = tracker.update(frame)

            if success:
                x, y, w, h = clamp_box(
                    int(raw[0]), int(raw[1]), int(raw[2]), int(raw[3])
                )
                raw_box      = (x, y, w, h)
                last_good_box = raw_box
                reinit_count  = 0

                # Kalman correction
                kalman.update(raw_box)
                vel = kalman.velocity()

                # EMA smooth display box
                smooth_box = smooth_ema(smooth_box, raw_box, BOX_SMOOTH)

                # Feature points for next-frame OF
                of_pts = detect_features(gray_raw, raw_box)

                # ── motion detection on smoothed ROI ──────────────
                sx, sy, sw, sh = smooth_box
                roi = gray_blur[sy:sy + sh, sx:sx + sw]
                if roi.size > 0:
                    if reference_f is None or reference_f.shape != roi.shape:
                        reference_f = roi.astype(np.float32)

                    roi_rs = cv2.resize(
                        roi, (reference_f.shape[1], reference_f.shape[0]),
                        interpolation=cv2.INTER_LINEAR,
                    )
                    ref_u8 = np.clip(reference_f, 0, 255).astype(np.uint8)
                    diff   = cv2.absdiff(ref_u8, roi_rs)
                    _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

                    motion_score = float(np.count_nonzero(thresh)) / thresh.size
                    motion_history.append(motion_score > MOTION_THRESHOLD)
                    cv2.accumulateWeighted(roi_rs.astype(np.float32),
                                           reference_f, ALPHA_REF)

                    is_moving = sum(motion_history) > len(motion_history) / 2
                    status = "MOVING" if is_moving else "STABLE"
                    color  = (0, 60, 255) if is_moving else (0, 220, 80)

            else:
                # ── CSRT failed → smart re-init ───────────────────
                can_reinit = (
                    last_good_box is not None
                    and reinit_count < MAX_REINIT
                    and (now - last_reinit_t) >= REINIT_COOLDOWN
                )

                if can_reinit:
                    # Build candidate box using Kalman + OF
                    if kalman_pred is not None:
                        px, py, pw, ph = kalman_pred
                    else:
                        px, py, pw, ph = last_good_box

                    # Shift by optical flow displacement
                    px = int(px + of_dx)
                    py = int(py + of_dy)

                    # Apply velocity look-ahead
                    vx, vy = vel
                    px = int(px + vx * VELOCITY_SCALE)
                    py = int(py + vy * VELOCITY_SCALE)

                    # Slightly expand box so CSRT has more context
                    candidate = expand_box(
                        clamp_box(px, py, pw, ph), SEARCH_EXPAND
                    )

                    print(f"[INFO] Re-init #{reinit_count + 1} at {candidate} "
                          f"(OF dx={of_dx:.1f} dy={of_dy:.1f}  "
                          f"vel vx={vx:.1f} vy={vy:.1f})")

                    new_t = init_tracker(frame, candidate)
                    if new_t is not None:
                        tracker      = new_t
                        reference_f  = None
                        motion_history.clear()
                        smooth_box   = candidate
                        of_pts       = detect_features(gray_raw, candidate)
                        reinit_count += 1
                        last_reinit_t = now
                        status = f"Re-tracking… ({reinit_count}/{MAX_REINIT})"
                        color  = (0, 180, 255)
                    else:
                        reinit_count += 1
                        last_reinit_t = now

                elif reinit_count >= MAX_REINIT:
                    print("[INFO] Max re-inits reached. Object declared lost.")
                    tracker       = None
                    kalman        = None
                    last_good_box = None
                    smooth_box    = None
                    of_pts        = None
                    reference_f   = None
                    motion_history.clear()
                    reinit_count  = 0
                    vel           = (0.0, 0.0)
                    status = "OBJECT LOST  —  Press [S] to reselect"
                    color  = (0, 60, 255)
                else:
                    status = "Searching…"
                    color  = (0, 180, 255)

        prev_gray = gray_raw.copy()

        # ── draw ─────────────────────────────────────────────────
        draw_overlay(frame, status, color, fps,
                     smooth_box, raw_box, motion_score, reinit_count, vel)
        cv2.imshow(WINDOW_NAME, frame)

        # ── keys ─────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key in (ord('s'), ord('S')):
            roi = cv2.selectROI(WINDOW_NAME, frame,
                                showCrosshair=True, fromCenter=False)
            if roi[2] > 15 and roi[3] > 15:
                box0 = (int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3]))
                new_t = init_tracker(frame, box0)
                if new_t is not None:
                    tracker       = new_t
                    kalman        = KalmanBoxTracker(box0)
                    last_good_box = box0
                    smooth_box    = box0
                    reference_f   = None
                    motion_history.clear()
                    reinit_count  = 0
                    vel           = (0.0, 0.0)
                    of_pts        = detect_features(gray_raw, box0)
                    print(f"[INFO] Tracker started on {box0}")
                else:
                    print("[ERROR] Init failed — try a different region or better lighting.")
            else:
                print("[WARN] ROI too small (need > 15×15 px).")

        elif key in (ord('r'), ord('R')):
            tracker = kalman = last_good_box = smooth_box = None
            reference_f = of_pts = None
            motion_history.clear()
            reinit_count = 0
            vel = (0.0, 0.0)
            print("[INFO] Reset.")

        elif key in (ord('q'), ord('Q')):
            print("[INFO] Quit.")
            break

        try:
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Done.")


if __name__ == "__main__":
    main()