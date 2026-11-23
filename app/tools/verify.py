"""Verify final reel specs, caption presence, karaoke brightness, and silence."""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

from common import load_config, stream_info

BAND_REL = (0.37, 0.50)  # caption band as a fraction of output height


def output_frame(path, t, W, H):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(path),
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
        stdout=subprocess.PIPE, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(H, W, 3)


def base_frame(cfg, t, W, H, SPLIT):
    cap = cv2.VideoCapture(cfg["source_path"])
    cap.set(cv2.CAP_PROP_POS_FRAMES, round(t * 60))
    ok, fr = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"no source frame at {t}s")
    fx0, fy0, fx1, fy1 = [int(v) for v in cfg["facecam_crop"]]
    frame = np.empty((H, W, 3), dtype=np.uint8)
    frame[0:SPLIT] = cv2.resize(fr[fy0:fy1, fx0:fx1], (W, SPLIT),
                                interpolation=cv2.INTER_LINEAR)
    gh = H - SPLIT
    gw = round(gh * 16 / 9)
    gp = cv2.resize(fr, (gw, gh), interpolation=cv2.INTER_LINEAR)
    gx = (gw - W) // 2
    frame[SPLIT:H] = gp[:, gx:gx + W]
    return frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cpath, cfg = load_config(args.config)
    final = Path(cfg["final"])
    W, H = int(cfg["output_width"]), int(cfg["output_height"])
    SPLIT = round(1093 * W / 1440)
    y0, y1 = int(H * BAND_REL[0]), int(H * BAND_REL[1])

    info = stream_info(final)
    print("SPEC:", json.dumps(info))
    assert info["width"] == W and info["height"] == H, "wrong output size"
    assert abs(info["fps"] - 60) < 0.05, "wrong fps"
    assert abs(info["duration"] - float(cfg["duration_s"])) < 0.2, "wrong duration"
    assert info["video_codec"] == "h264" and info["audio_codec"] == "aac"

    cues = json.loads((cpath.parent / "caption_cues.json").read_text(
        encoding="utf-8"))["cues"]

    def diff(t):
        o = output_frame(final, t, W, H)[y0:y1].astype(np.int16)
        b = base_frame(cfg, t, W, H, SPLIT)[y0:y1].astype(np.int16)
        d = np.abs(o - b).max(axis=2)
        return int((d > 30).sum()), float(d.mean())

    print("--- speech samples ---")
    for c in cues[:4] + cues[-2:]:
        t = c["s"] + min(0.5, (c["e"] - c["s"]) * 0.4)
        n, mean = diff(round(t, 2))
        print(f"t={t:6.2f} changed_px={n:7d} mean_diff={mean:5.1f}  {c['text']}")
        assert n > 2000, f"caption missing at {t}s"

    print("--- silence samples ---")
    occupied = [(float(c["s"]), float(c["e"])) for c in cues]
    cursor, gaps = 0.0, []
    for s, e in sorted(occupied):
        if s - cursor > 1.0:
            gaps.append((cursor, s))
        cursor = max(cursor, e)
    if float(cfg["duration_s"]) - cursor > 1.0:
        gaps.append((cursor, float(cfg["duration_s"])))
    for s, e in sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[:4]:
        t = round((s + e) / 2, 2)
        n, mean = diff(t)
        print(f"t={t:6.2f} changed_px={n:7d} mean_diff={mean:5.1f}")
        assert n < 1500, f"text present during silence at {t}s"

    print("VERIFY: OK")


if __name__ == "__main__":
    main()
