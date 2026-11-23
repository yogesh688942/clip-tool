"""Helpers shared by all clip-tool scripts."""
import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
LIB = TOOLS.parent / "lib"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from paths import ROOT, PROJECTS, DOWNLOADS  # noqa: E402


def load_config(path):
    path = Path(path).resolve()
    return path, json.loads(path.read_text(encoding="utf-8"))


def save_config(path, cfg):
    Path(path).write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")


def parse_time(value):
    """'01:58:27', '1:58:27', '58:27', '63.5', or 63.5 -> seconds."""
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if ":" in s:
        parts = [float(p) for p in s.split(":")]
        total = 0.0
        for p in parts:
            total = total * 60 + p
        return total
    return float(s)


def hms(seconds):
    seconds = int(round(float(seconds)))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def run(cmd, **kwargs):
    """Run a command, decoding output as text and raising on failure."""
    return subprocess.run([str(c) for c in cmd], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, encoding="utf-8", errors="replace", **kwargs)


def ffprobe(path):
    out = run([
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", path,
    ]).stdout
    return json.loads(out)


def stream_info(path):
    info = ffprobe(path)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        raise RuntimeError("no video stream in " + str(path))
    num, den = (v.get("r_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0.0
    return {
        "width": int(v["width"]),
        "height": int(v["height"]),
        "fps": round(fps, 3),
        "duration": float(info["format"]["duration"]),
        "video_codec": v.get("codec_name"),
        "audio_codec": a.get("codec_name") if a else None,
        "size": int(info["format"].get("size", 0)),
    }
