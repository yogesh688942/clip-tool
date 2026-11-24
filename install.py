"""One-command installer for the clip tool and its OpenCode skills/command.

Run with:  python install.py
Safe to re-run. Creates .venv, installs dependencies (including Earshot with
its listening + MCP extras), checks ffmpeg, and registers the global OpenCode
skills (clip tool, openverse, real-sfx, real-sound, earshot) + '/clip' command.

Set CLIP_TOOL_EARSHOT_FETCH=1 before running to pre-download Earshot's ~1.1 GB
listening models. Otherwise they download on first listening use.
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
    skills_src = ROOT / ".opencode" / "skills"
    cmd_src = ROOT / ".opencode" / "commands" / "clip.md"

    cmd_dst = op / "commands" / "clip.md"
    cmd_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cmd_src, cmd_dst)
    print(f"OpenCode command: {cmd_dst}", flush=True)

    # Copy every bundled skill folder (workflow + the three sound tools).
    installed = []
    for skill in sorted(p for p in skills_src.iterdir() if p.is_dir()):
        if not (skill / "SKILL.md").exists():
            continue
        dst = op / "skills" / skill.name
        shutil.copytree(skill, dst, dirs_exist_ok=True)
        installed.append(skill.name)
        print(f"OpenCode skill: {dst / 'SKILL.md'}", flush=True)

    # The skills are installed globally, so they need to know where the repo lives.
    (op / "clip-tool-path.txt").write_text(str(ROOT) + "\n", encoding="utf-8")
    return installed


def prepare_torch(py):
    """Earshot's listen extra needs torch; use the small CPU wheel index first."""
    print("installing CPU-only PyTorch first (keeps Earshot download small)...", flush=True)
    try:
        call([py, "-m", "pip", "install", "torch",
              "--index-url", "https://download.pytorch.org/whl/cpu"])
    except Exception as e:
        print("CPU torch pre-install failed; using the default index:", e, flush=True)


def check_sound_tools(py):
    try:
        out = subprocess.check_output([py, "-m", "earshot", "doctor"],
                                      text=True, stderr=subprocess.STDOUT)
        print(out.strip(), flush=True)
    except Exception as e:
        print("Earshot doctor could not run yet:", e, flush=True)

    if os.environ.get("CLIP_TOOL_EARSHOT_FETCH") == "1":
        print("pre-fetching Earshot listening models (~1.1 GB)...", flush=True)
        call([py, "-m", "earshot", "doctor", "--fetch"])
    else:
        print(
            "Earshot listening models download on first use (~1.1 GB). To fetch "
            "them now, set CLIP_TOOL_EARSHOT_FETCH=1 and re-run install.py.",
            flush=True,
        )


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
    prepare_torch(py)
    call([py, "-m", "pip", "install", "-r", ROOT / "requirements.txt"])
    ensure_ffmpeg()
    check_sound_tools(py)

    check = (
        "import whisper, cv2, numpy, PIL, yt_dlp; "
        "print('IMPORTS OK', whisper.__version__ if hasattr(whisper,'__version__') else '')"
    )
    out = subprocess.check_output([py, "-c", check], text=True)
    print(out.strip(), flush=True)

    # Pre-download the Whisper small model so the first clip does not stall.
    print("pre-downloading Whisper 'small' model (one time)...", flush=True)
    subprocess.check_call([py, "-c", "import whisper; whisper.load_model('small')"])

    skills = register_opencode()
    (ROOT / "installed.json").write_text(json.dumps({
        "python": str(py), "platform": SYSTEM, "root": str(ROOT),
        "opencode_skills": skills,
        "sound_tools": ["openverse", "real-sfx", "real-sound", "earshot"],
    }, indent=2) + "\n", encoding="utf-8")
    print("CLIP TOOL READY", flush=True)


if __name__ == "__main__":
    main()
