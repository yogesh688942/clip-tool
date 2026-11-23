"""Final render: exact-duration vertical reel, facecam top + gameplay bottom.

Supports the two approved caption profiles:
  full_cue_fade     - whole cue at once with 0.10s fades (saved default)
  karaoke_highlight - whole cue dimmed, each word eases up at its word time

PIL overlays are RGB; cv2 frames are BGR. Composite in RGB, convert back.
"""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from common import load_config, save_config, run
from paths import DOWNLOADS

FADE = 0.10
HL_TIME = 0.18
SPLIT_BASE = 1093
SPLIT_W_BASE = 1440


def smoothstep(p):
    p = max(0.0, min(1.0, p))
    return p * p * (3.0 - 2.0 * p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cpath, cfg = load_config(args.config)
    pdir = cpath.parent
    cues_path = pdir / "caption_cues.json"
    cues = json.loads(cues_path.read_text(encoding="utf-8"))["cues"]

    if not cfg.get("facecam_crop"):
        raise SystemExit("facecam_crop is not set")
    W = int(cfg.get("output_width", 1440))
    H = int(cfg.get("output_height", 2560))
    FPS = 60
    SPLIT = round(SPLIT_BASE * W / SPLIT_W_BASE)
    CAP_SCALE = W / 1080
    DUR = float(cfg["duration_s"])
    profile = cfg.get("caption_profile", "full_cue_fade")
    if profile == "word_by_word_reveal":
        raise SystemExit("word_by_word_reveal is deprecated - do not use")
    if profile not in ("full_cue_fade", "karaoke_highlight"):
        raise SystemExit(f"unknown caption profile: {profile}")

    # ---- Overlays ----
    if profile == "karaoke_highlight":
        from karaoke_caption import build_karaoke
        overlays = {c["i"]: build_karaoke(c, scale=CAP_SCALE, split=820, W=W, H=H)
                    for c in cues}
    else:
        from emoji_text import render_cue
        overlays = {}
        for c in cues:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            render_cue(layer, c, scale=CAP_SCALE, split=820)
            arr = np.array(layer)
            ys, xs = np.where(arr[:, :, 3] > 0)
            if len(ys):
                y0, y1 = int(ys.min()), int(ys.max()) + 1
                x0, x1 = int(xs.min()), int(xs.max()) + 1
                overlays[c["i"]] = {"y0": y0, "x0": x0,
                                    "base": arr[y0:y1, x0:x1], "highlights": []}
            else:
                overlays[c["i"]] = None
    print(f"overlays: {sum(1 for v in overlays.values() if v)} / {len(cues)} "
          f"| profile={profile}", flush=True)

    # ---- Video ----
    video_tmp = pdir / "video_only.mp4"
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", video_tmp,
    ]
    proc = subprocess.Popen([str(c) for c in cmd], stdin=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    cap = cv2.VideoCapture(cfg["source_path"])
    fx0, fy0, fx1, fy1 = [int(v) for v in cfg["facecam_crop"]]
    total = int(round(DUR * FPS))
    gh = H - SPLIT
    gw = round(gh * 16 / 9)
    gx = (gw - W) // 2

    for k in range(total):
        ok, fr = cap.read()
        if not ok:
            break
        frame = np.empty((H, W, 3), dtype=np.uint8)
        frame[0:SPLIT] = cv2.resize(
            fr[fy0:fy1, fx0:fx1], (W, SPLIT), interpolation=cv2.INTER_LINEAR)
        gp = cv2.resize(fr, (gw, gh), interpolation=cv2.INTER_LINEAR)
        frame[SPLIT:H] = gp[:, gx:gx + W]

        t = k / FPS
        cue = next((c for c in cues if c["s"] <= t <= c["e"]), None)
        if cue:
            ov = overlays.get(cue["i"])
            if ov:
                fade = max(0.0, min(1.0, (t - cue["s"]) / FADE,
                                    (cue["e"] - t) / FADE))
                y0, x0 = ov["y0"], ov["x0"]
                base = ov["base"]
                h, w = base.shape[:2]
                # Composite in RGB space.
                comp = cv2.cvtColor(frame[y0:y0 + h, x0:x0 + w],
                                    cv2.COLOR_BGR2RGB).astype(np.float32)
                ba = (base[:, :, 3:4].astype(np.float32) / 255.0) * fade
                comp = comp * (1 - ba) + base[:, :, :3].astype(np.float32) * ba
                for hl in ov["highlights"]:
                    p = smoothstep((t - hl["t"]) / HL_TIME)
                    if p <= 0:
                        continue
                    hy, hx = hl["y"], hl["x"]
                    ea = hl["arr"]
                    eh, ew = ea.shape[:2]
                    a = (ea[:, :, 3:4].astype(np.float32) / 255.0) * p * fade
                    sub = comp[hy:hy + eh, hx:hx + ew]
                    comp[hy:hy + eh, hx:hx + ew] = (
                        sub * (1 - a) + ea[:, :, :3].astype(np.float32) * a)
                frame[y0:y0 + h, x0:x0 + w] = cv2.cvtColor(
                    np.clip(comp, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        proc.stdin.write(frame.tobytes())
        if k % 600 == 0:
            print(f"frame {k}/{total} ({t:.1f}s)", flush=True)
    cap.release()
    proc.stdin.close()
    proc.wait()
    print("video done", flush=True)

    # ---- Audio + mux ----
    from audio import build_audio
    audio_path = build_audio(cfg, pdir, DUR)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    final = DOWNLOADS / Path(cfg["output"]).name
    run(["ffmpeg", "-y", "-i", video_tmp, "-i", audio_path,
         "-c", "copy", "-movflags", "+faststart", final])
    cfg["status"] = "rendered"
    cfg["final"] = str(final)
    save_config(cpath, cfg)
    print("FINAL:", final, flush=True)


if __name__ == "__main__":
    main()
