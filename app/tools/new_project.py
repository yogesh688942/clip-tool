"""Create a new clip project config from a URL and timestamp range."""
import argparse
import json
from pathlib import Path

from common import PROJECTS, parse_time, hms


def slug_for(seconds):
    return hms(seconds).replace(":", "-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--name", default=None)
    ap.add_argument("--profile", default="full_cue_fade",
                    choices=["full_cue_fade", "karaoke_highlight"])
    args = ap.parse_args()

    start_s, end_s = parse_time(args.start), parse_time(args.end)
    if end_s <= start_s:
        raise SystemExit("end must be after start")
    slug = slug_for(start_s)
    name = args.name or f"stream_{slug}"
    pdir = PROJECTS / name
    pdir.mkdir(parents=True, exist_ok=True)

    suffix = "_karaoke" if args.profile == "karaoke_highlight" else ""
    cfg = {
        "name": name,
        "url": args.url,
        "start": hms(start_s),
        "end": hms(end_s),
        "duration_s": round(end_s - start_s, 3),
        "caption_profile": args.profile,
        "facecam_crop": None,
        "gameplay_crop_x": None,
        "split_y": None,
        "sfx_events": [],
        "source_info": None,
        "output": f"downloads/reel_{slug}_1440p60_hinglish{suffix}.mp4",
        "status": "created",
    }
    cpath = pdir / "config.json"
    cpath.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    print(json.dumps({"config": str(cpath), "project": str(pdir),
                      "duration_s": cfg["duration_s"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
