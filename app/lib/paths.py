"""Shared, portable paths for the clip tool.

All paths are resolved relative to the repository root, never to a fixed
Windows user directory, so the repo works on any machine.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app"
LIB = APP / "lib"
TOOLS = APP / "tools"
DOCS = APP / "docs"
PRESETS = APP / "presets"
ASSETS = APP / "assets"
FONT_DIR = ASSETS / "fonts"
EMOJI_DIR = ASSETS / "emoji"
SFX_DIR = APP / "sfx" / "meme"
PROJECTS = ROOT / "projects"
DOWNLOADS = ROOT / "downloads"


def project_dir(name):
    return PROJECTS / name


def ensure_dirs():
    for p in (PROJECTS, DOWNLOADS, EMOJI_DIR, SFX_DIR):
        p.mkdir(parents=True, exist_ok=True)
