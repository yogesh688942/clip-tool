"""Transcribe speech with word timestamps, with a forced pass for loud game audio."""
import argparse
import json
import re
from pathlib import Path

from common import load_config, save_config


def clean_words(result):
    words = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            text = (w.get("word") or "").strip()
            if not text:
                continue
            words.append({"w": text, "s": round(float(w["start"]), 2),
                          "e": round(float(w["end"]), 2)})
    return words


def merge_words(primary, secondary):
    """Add non-overlapping words from the secondary pass to fill missed speech."""
    out = [dict(w) for w in primary]
    for w in secondary:
        if not re.search(r"[A-Za-z]", w["w"]) or len(w["w"]) > 20:
            continue
        if any(abs(w["s"] - p["s"]) < 0.28 for p in out):
            continue
        out.append(dict(w))
    out.sort(key=lambda w: w["s"])
    return out


def to_segments(result):
    segs = []
    for s in result.get("segments", []):
        segs.append({
            "start": round(float(s["start"]), 2),
            "end": round(float(s["end"]), 2),
            "text": (s.get("text") or "").strip(),
        })
    return segs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cpath, cfg = load_config(args.config)
    pdir = cpath.parent
    src = Path(cfg["source_path"])
    duration = float(cfg["duration_s"])

    import whisper
    model = whisper.load_model("small")

    normal = model.transcribe(str(src), word_timestamps=True, language="en")
    words = clean_words(normal)
    used = "normal"
    forced = None

    if len(words) < max(6, duration / 8) or len((normal.get("text") or "").strip()) < 15:
        print("normal pass found little speech - running forced pass", flush=True)
        forced = model.transcribe(
            str(src), word_timestamps=True, language="en",
            no_speech_threshold=0.95, condition_on_previous_text=False,
        )
        fw = clean_words(forced)
        if len(fw) > len(words):
            words = merge_words(fw, words)
            used = "forced_merged"
    else:
        # Always keep the forced result available for gap filling on noisy clips.
        forced = model.transcribe(
            str(src), word_timestamps=True, language="en",
            no_speech_threshold=0.95, condition_on_previous_text=False,
        )
        fw = clean_words(forced)
        before = len(words)
        words = merge_words(words, fw)
        if len(words) > before:
            used = "normal_merged"

    data = {
        "duration": duration,
        "pass_used": used,
        "text": normal.get("text", ""),
        "segments": to_segments(normal),
        "words": words,
    }
    out = pdir / "transcript.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")

    cfg["transcript"] = str(out)
    cfg["status"] = "transcribed"
    save_config(cpath, cfg)

    print(f"transcript: {out} | pass={used} | words={len(words)}", flush=True)
    for i, s in enumerate(data["segments"]):
        print(f"[{i:02d}] {s['start']:6.2f}-{s['end']:6.2f}  {s['text']}", flush=True)


if __name__ == "__main__":
    main()
