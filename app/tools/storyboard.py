"""Build the approval storyboard: one frame per cue plus silence samples."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import load_config

PW, PH = 360, 640
SCALE = PW / 1080
SPLIT_BASE = 820
SPLIT_PX = int(SPLIT_BASE * SCALE)
LBL, COLS = 24, 6


def font(size=12):
    for p in (r"C:\Windows\Fonts\arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cpath, cfg = load_config(args.config)
    pdir = cpath.parent
    cues_path = pdir / "caption_cues.json"
    if not cues_path.exists():
        raise SystemExit("caption_cues.json is missing - translate the transcript first")
    cues = json.loads(cues_path.read_text(encoding="utf-8"))["cues"]
    if not cfg.get("facecam_crop"):
        raise SystemExit("facecam_crop is not set in config - confirm it first")

    duration = float(cfg["duration_s"])
    times = []
    for c in cues:
        t = c["s"] + min(1.0, (c["e"] - c["s"]) * 0.35)
        times.append(round(t, 2))
    # Silence samples: midpoints of the largest gaps.
    occupied = [(float(c["s"]), float(c["e"])) for c in cues]
    cursor = 0.0
    gaps = []
    for s, e in sorted(occupied):
        if s - cursor > 0.8:
            gaps.append((cursor, s))
        cursor = max(cursor, e)
    if duration - cursor > 0.8:
        gaps.append((cursor, duration))
    for s, e in sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[:5]:
        times.append(round((s + e) / 2, 2))
    times = sorted(set(times))[:30]

    cap = cv2.VideoCapture(cfg["source_path"])
    rows = (len(times) + COLS - 1) // COLS
    sheet = Image.new("RGB", (PW * COLS, (PH + LBL) * rows), (12, 12, 12))
    ds = ImageDraw.Draw(sheet)
    fx0, fy0, fx1, fy1 = [int(v) for v in cfg["facecam_crop"]]

    for idx, t in enumerate(times):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, bgr = cap.read()
        if not ok:
            continue
        src = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        sw, sh = src.size
        panel = Image.new("RGB", (PW, PH), (8, 8, 8))
        # Upper panel: facecam, edge to edge.
        panel.paste(src.crop((fx0, fy0, fx1, fy1)).resize(
            (PW, SPLIT_PX), Image.Resampling.LANCZOS), (0, 0))
        # Lower panel: tight centre crop of the gameplay.
        gh = PH - SPLIT_PX
        gw = round(gh * 16 / 9)
        gp = src.resize((gw, gh), Image.Resampling.LANCZOS)
        left = (gw - PW) // 2
        panel.paste(gp.crop((left, 0, left + PW, gh)), (0, SPLIT_PX))

        cue = next((c for c in cues if c["s"] <= t <= c["e"]), None)
        if cue:
            from emoji_text import render_cue
            layer = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
            render_cue(layer, cue, scale=SCALE, split=SPLIT_BASE)
            panel = Image.alpha_composite(panel.convert("RGBA"), layer).convert("RGB")
            status = "SPEECH"
        else:
            ImageDraw.Draw(panel).text(
                (PW // 2, SPLIT_PX + 14), "(silence - no text)",
                font=font(12), fill="#9AA0A6", anchor="mm")
            status = "SILENCE"

        x, y = (idx % COLS) * PW, (idx // COLS) * (PH + LBL)
        sheet.paste(panel, (x, y + LBL))
        ds.rectangle((x, y, x + PW, y + LBL), fill=(24, 24, 24))
        ds.text((x + 4, y + 5), f"{t:05.2f}s  {status}", font=font(12),
                fill=(255, 255, 255))
    cap.release()

    out = pdir / "storyboard.jpg"
    sheet.save(out, quality=92)
    print(json.dumps({"storyboard": str(out), "frames": len(times)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
