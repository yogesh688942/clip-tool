"""One-command installer for the clip tool and its OpenCode skill/command.

Run with:  python install.py
Safe to re-run. Creates .venv, installs dependencies, checks ffmpeg, and
registers the global OpenCode skill + '/clip' command.
"""
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
SYSTEM = platform.system()


def venv_python():
    if SYSTEM == "Windows":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def call(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.check_call([str(c) for c in cmd], **kw)


def ensure_ffmpeg():
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        print("ffmpeg/ffprobe: already available", flush=True)
        return True
    print("ffmpeg not found - attempting install", flush=True)
    try:
        if SYSTEM == "Windows":
            call(["winget", "install", "--id", "Gyan.FFmpeg", "-e",
                  "--accept-source-agreements", "--accept-package-agreements"])
        elif SYSTEM == "Darwin":
            call(["brew", "install", "ffmpeg"])
        else:
            if shutil.which("sudo"):
                call(["sudo", "apt-get", "update"])
                call(["sudo", "apt-get", "install", "-y", "ffmpeg"])
            else:
                call(["apt-get", "install", "-y", "ffmpeg"])
    except Exception as e:
        print("ffmpeg auto-install failed:", e, flush=True)
    ok = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
    if not ok:
        print(
            "WARNING: ffmpeg/ffprobe were not found on PATH. Install them manually "
            "(https://ffmpeg.org/download.html) and re-run install.py. The bundled "
            "imageio-ffmpeg binary can be used as a fallback by setting PATH.",
            flush=True,
        )
    return ok


def register_opencode():
    home = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    op = home / "opencode"
    skill_src = ROOT / ".opencode" / "skills" / "clip-tool" / "SKILL.md"
    cmd_src = ROOT / ".opencode" / "commands" / "clip.md"

    skill_dst = op / "skills" / "clip-tool" / "SKILL.md"
    cmd_dst = op / "commands" / "clip.md"
    skill_dst.parent.mkdir(parents=True, exist_ok=True)
    cmd_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(skill_src, skill_dst)
    shutil.copyfile(cmd_src, cmd_dst)

    # The skill is installed globally, so it needs to know where the repo lives.
    (op / "clip-tool-path.txt").write_text(str(ROOT) + "\n", encoding="utf-8")
    print(f"OpenCode skill: {skill_dst}", flush=True)
    print(f"OpenCode command: {cmd_dst}", flush=True)


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 or newer is required")
    print(f"installing clip tool from {ROOT}", flush=True)

    if not VENV.exists():
        call([sys.executable, "-m", "venv", VENV])
    py = venv_python()
    if not py.exists():
        raise SystemExit(f"venv python missing: {py}")

    call([py, "-m", "pip", "install", "--upgrade", "pip"])
    call([py, "-m", "pip", "install", "-r", ROOT / "requirements.txt"])
    ensure_ffmpeg()

    check = (
        "import whisper, cv2, numpy, PIL, yt_dlp; "
        "print('IMPORTS OK', whisper.__version__ if hasattr(whisper,'__version__') else '')"
    )
    out = subprocess.check_output([py, "-c", check], text=True)
    print(out.strip(), flush=True)

    # Pre-download the Whisper small model so the first clip does not stall.
    print("pre-downloading Whisper 'small' model (one time)...", flush=True)
    subprocess.check_call([py, "-c", "import whisper; whisper.load_model('small')"])

    register_opencode()
    (ROOT / "installed.json").write_text(json.dumps({
        "python": str(py), "platform": SYSTEM, "root": str(ROOT),
    }, indent=2) + "\n", encoding="utf-8")
    print("CLIP TOOL READY", flush=True)


if __name__ == "__main__":
    main()
