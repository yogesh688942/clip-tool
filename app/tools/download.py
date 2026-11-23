"""Download the exact requested section at the highest available 60fps resolution.

NEVER cut, re-time or shorten afterwards: the downloaded duration must equal
the requested timestamp difference.
"""
import argparse
import json
from pathlib import Path

from common import load_config, save_config, run, stream_info, hms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cpath, cfg = load_config(args.config)
    pdir = cpath.parent

    section = f"*{cfg['start']}-{cfg['end']}"
    outtmpl = str(pdir / "source.%(ext)s")
    fmt = "bestvideo[fps>=60]+bestaudio/bestvideo+bestaudio"
    cmd = [
        "yt-dlp", "--no-playlist", "--download-sections", section,
        "--force-keyframes-at-cuts", "-f", fmt,
        "--merge-output-format", "mp4", "-o", outtmpl, cfg["url"],
    ]
    print("download:", " ".join(cmd), flush=True)
    proc = run(cmd)
    print(proc.stdout[-3000:], flush=True)

    candidates = sorted(pdir.glob("source.*"))
    candidates = [p for p in candidates if p.suffix.lower() in
                  (".mp4", ".mkv", ".webm", ".mov")]
    if not candidates:
        raise SystemExit("download produced no source file")
    src = candidates[0]
    src_mp4 = pdir / "source.mp4"
    if src.suffix.lower() != ".mp4":
        run(["ffmpeg", "-y", "-i", src, "-c", "copy", src_mp4])
        src = src_mp4

    info = stream_info(src)
    expected = float(cfg["duration_s"])
    if abs(info["duration"] - expected) > 0.6:
        raise SystemExit(
            f"duration mismatch: got {info['duration']:.3f}s, expected {expected:.3f}s"
        )
    if info["fps"] < 59:
        raise SystemExit(f"source is not 60fps: {info['fps']}")

    if info["width"] >= 3840:
        cfg["output_width"], cfg["output_height"] = 2160, 3840
        cfg["output"] = cfg["output"].replace("_1440p60_", "_2160p60_")
    else:
        cfg["output_width"], cfg["output_height"] = 1440, 2560

    cfg["source_info"] = info
    cfg["source_path"] = str(src)
    cfg["status"] = "downloaded"
    save_config(cpath, cfg)
    print(json.dumps({"config": str(cpath), "source": str(src),
                      "info": info,
                      "output_size": [cfg["output_width"], cfg["output_height"]]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
