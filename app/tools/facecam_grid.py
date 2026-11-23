"""Detect the facecam per clip and produce labeled grids for user confirmation."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import load_config, save_config

LABEL_FONT = ImageFont.truetype("arial.ttf", 13) if Path(
    r"C:\Windows\Fonts\arial.ttf").exists() else ImageFont.load_default()


def font(size=13):
    for p in (r"C:\Windows\Fonts\arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def read_frame(cap, t):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, bgr = cap.read()
    return bgr if ok else None


def detect_faces(bgr, cascades):
    eq = cv2.equalizeHist(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY))
    found = []
    for cas, sf, mn in cascades:
        for x, y, w, h in cas.detectMultiScale(
                eq, scaleFactor=sf, minNeighbors=mn,
                minSize=(45, 45), maxSize=(320, 320)):
            found.append((int(x), int(y), int(w), int(h)))
    uniq = []
    for box in found:
        cx, cy = box[0] + box[2] / 2, box[1] + box[3] / 2
        if not any(abs(cx - (u[0] + u[2] / 2)) < 40 and
                   abs(cy - (u[1] + u[3] / 2)) < 40 for u in uniq):
            uniq.append(box)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cpath, cfg = load_config(args.config)
    pdir = cpath.parent
    src = Path(cfg["source_path"])
    duration = float(cfg["duration_s"])

    base = cv2.data.haarcascades
    cascades = [
        (cv2.CascadeClassifier(base + "haarcascade_frontalface_default.xml"), 1.08, 4),
        (cv2.CascadeClassifier(base + "haarcascade_frontalface_alt2.xml"), 1.08, 3),
    ]

    cap = cv2.VideoCapture(str(src))
    times = list(np.linspace(1.0, max(2.0, duration - 1.0), 10))
    clusters = defaultdict(list)
    frames = {}
    for t in times:
        bgr = read_frame(cap, float(t))
        if bgr is None:
            continue
        frames[round(float(t), 2)] = bgr.copy()
        h, w = bgr.shape[:2]
        for x, y, fw, fh in detect_faces(bgr, cascades):
            cx, cy = x + fw / 2, y + fh / 2
            key = (round(cx / 70), round(cy / 70))
            clusters[key].append((x, y, fw, fh, w, h, float(t)))
    cap.release()

    ranked = []
    for key, hits in clusters.items():
        if len(hits) < 2:
            continue
        xs = [h[0] for h in hits]
        ys = [h[1] for h in hits]
        ws_ = [h[2] for h in hits]
        hs_ = [h[3] for h in hits]
        fw, fh = int(np.median(ws_)), int(np.median(hs_))
        cx, cy = int(np.median([h[0] + h[2] / 2 for h in hits])), int(
            np.median([h[1] + h[3] / 2 for h in hits]))
        W, H = hits[0][4], hits[0][5]
        bw, bh = int(fw * 1.6), int(fh * 1.6)
        box = [max(0, cx - bw // 2), max(0, cy - bh // 2),
               min(W, cx + bw // 2), min(H, cy + bh // 2)]
        score = len(hits) * (fw * fh) ** 0.5
        ranked.append({"center": [cx, cy], "crop": box, "hits": len(hits),
                       "score": round(score, 1)})
    ranked.sort(key=lambda r: r["score"], reverse=True)
    ranked = ranked[:6]

    if not frames:
        raise SystemExit("could not read any frames")

    # Sheet 1: full frames with 10% grid and source coordinates.
    PW, PH, LBL, COLS = 480, 270, 24, 2
    items = list(frames.items())[:8]
    rows = (len(items) + COLS - 1) // COLS
    sheet = Image.new("RGB", (PW * COLS, (PH + LBL) * rows), (10, 10, 10))
    d = ImageDraw.Draw(sheet)
    for i, (t, bgr) in enumerate(items):
        H, W = bgr.shape[:2]
        im = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).resize((PW, PH))
        gd = ImageDraw.Draw(im)
        for frac in range(1, 10):
            x = int(PW * frac / 10)
            gd.line((x, 0, x, PH), fill=(255, 255, 0), width=1)
            gd.text((x + 2, 2), str(round(W * frac / 10)), fill=(255, 255, 0), font=font(10))
            y = int(PH * frac / 10)
            gd.line((0, y, PW, y), fill=(255, 255, 0), width=1)
            gd.text((2, y + 1), str(round(H * frac / 10)), fill=(255, 255, 0), font=font(10))
        x0, y0 = (i % COLS) * PW, (i // COLS) * (PH + LBL)
        sheet.paste(im, (x0, y0 + LBL))
        d.rectangle((x0, y0, x0 + PW, y0 + LBL), fill=(25, 25, 25))
        d.text((x0 + 5, y0 + 5), f"t={t:.2f}s   source {W}x{H}",
               fill=(255, 255, 255), font=font(13))
    grid_path = pdir / "facecam_grid.jpg"
    sheet.save(grid_path, quality=92)

    # Sheet 2: candidate crops from a representative frame.
    mid_t = items[len(items) // 2][0]
    bgr = frames[mid_t]
    H, W = bgr.shape[:2]
    CPW, CPH, CC = 420, 320, 3
    rows = (len(ranked) + CC - 1) // CC
    sheet2 = Image.new("RGB", (CPW * CC, (CPH + LBL) * rows), (10, 10, 10))
    d2 = ImageDraw.Draw(sheet2)
    for i, cand in enumerate(ranked):
        x1, y1, x2, y2 = cand["crop"]
        crop = bgr[max(0, y1):min(H, y2), max(0, x1):min(W, x2)]
        if crop.size == 0:
            continue
        im = Image.fromarray(cv2.cvtColor(
            cv2.resize(crop, (CPW, CPH), interpolation=cv2.INTER_LINEAR),
            cv2.COLOR_BGR2RGB))
        x0, y0 = (i % CC) * CPW, (i // CC) * (CPH + LBL)
        sheet2.paste(im, (x0, y0 + LBL))
        d2.rectangle((x0, y0, x0 + CPW, y0 + LBL), fill=(25, 25, 25))
        d2.text((x0 + 4, y0 + 5),
                f"{i}: {cand['crop']}  hits={cand['hits']}",
                fill=(255, 255, 255), font=font(12))
    cand_path = pdir / "facecam_candidates.jpg"
    sheet2.save(cand_path, quality=92)

    data = {"grid": str(grid_path), "candidates_image": str(cand_path),
            "source_size": [W, H], "candidates": ranked}
    (pdir / "facecam_candidates.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8")
    cfg["facecam_grid"] = str(grid_path)
    cfg["status"] = "facecam_detected"
    save_config(cpath, cfg)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
