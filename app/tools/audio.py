"""Voice + sparse MyInstants meme SFX mix. No beat, no music bed."""
import re
import subprocess
import wave
import urllib.request
from pathlib import Path

import numpy as np

from common import run
from paths import SFX_DIR

SR = 48000
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def ensure_sfx(name):
    path = SFX_DIR / f"{name}.mp3"
    if path.exists() and path.stat().st_size > 0:
        return path
    url = f"https://www.myinstants.com/en/instant/{name}/"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r"(/media/sounds/[^\"']+?\.mp3)", html)
    if not m:
        raise RuntimeError(f"no mp3 found on MyInstants page for {name}")
    media = "https://www.myinstants.com" + m.group(1)
    req = urllib.request.Request(media, headers={"User-Agent": UA})
    path.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    return path


def decode(path, max_len=None):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
         "-f", "f32le", "-"],
        stdout=subprocess.PIPE, check=True,
    ).stdout
    a = np.frombuffer(out, dtype=np.float32).copy()
    return a[:round(max_len * SR)] if max_len else a


def build_audio(cfg, pdir, duration):
    events = cfg.get("sfx_events") or []
    track = np.zeros(round(duration * SR), dtype=np.float32)
    for ev in events:
        if isinstance(ev, (list, tuple)):
            t, name, max_len, gain = (list(ev) + [None, 0.5])[:4]
        else:
            t, name = float(ev["t"]), ev["name"]
            max_len, gain = ev.get("max_len"), ev.get("gain", 0.5)
        t = float(t)
        path = ensure_sfx(name)
        data = decode(path, max_len)
        start = round(t * SR)
        n = min(len(data), len(track) - start)
        if n > 0:
            track[start:start + n] += data[:n] * float(gain)
            print(f"sfx {t:6.2f}s {name:<18} {n / SR:.2f}s", flush=True)

    wav_path = pdir / "meme_sfx_track.wav"
    with wave.open(str(wav_path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes())

    af = (
        f"[0:a]atrim=duration={duration},loudnorm=I=-14:TP=-1.5:LRA=11[voice];"
        f"[1:a]atrim=duration={duration},volume=0.85[sfx];"
        f"[voice][sfx]amix=inputs=2:duration=first:normalize=0,"
        f"atrim=duration={duration}[out]"
    )
    audio_path = pdir / "audio.m4a"
    run(["ffmpeg", "-y", "-i", cfg["source_path"], "-i", wav_path,
         "-filter_complex", af, "-map", "[out]", "-c:a", "aac", "-b:a", "192k",
         audio_path])
    print("audio mix done", flush=True)
    return audio_path
