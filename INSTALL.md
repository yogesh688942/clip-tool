# Installation instructions (for OpenCode to follow)

The user will ask you to install this repo on a new computer using OpenCode.
Do the following in order. Do not ask the user to run manual terminal commands.

1. Clone the repo into a stable folder:
   - Windows: `Documents\clip-tool`
   - macOS/Linux: `~/clip-tool`
   Use `git clone https://github.com/yogesh688942/clip-tool.git <destination>`. If the destination
   already exists and is a git checkout, run `git pull` instead.

2. Verify `python --version` is 3.10+. If not, install Python 3.12 from
   <https://www.python.org/downloads/> (Windows: check "Add Python to PATH").

3. From the repo root run:
   ```sh
   python install.py
   ```
   This creates `.venv`, installs CPU-only PyTorch then `requirements.txt`
   (Whisper, OpenCV and Earshot with its `listen` + `mcp` extras),
   installs/verifies ffmpeg, pre-downloads the Whisper `small` model, and copies
   every bundled skill (`clip-tool`, `openverse`, `real-sfx`, `real-sound`,
   `earshot`) plus the `/clip` command into the global OpenCode config directory.

   Git must be installed (Earshot is fetched from GitHub). The first install
   pulls roughly 1.5 GB: Whisper ~500 MB, CPU PyTorch + Earshot, then ~1.1 GB of
   listening models on first use.

4. If ffmpeg is still not on PATH after `install.py`, install it:
   - Windows: `winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements`
   - macOS: `brew install ffmpeg`
   - Debian/Ubuntu: `sudo apt-get install -y ffmpeg`
   Then re-run `python install.py`.

5. Confirm the install by checking that `.venv`, `app/tools`, `app/assets/emoji`,
   `app/sfx/meme`, and that the global OpenCode config directory contains
   `clip-tool-path.txt`, `commands/clip.md`, and `skills/` folders named
   `clip-tool`, `openverse`, `real-sfx`, `real-sound` and `earshot` (each with a
   `SKILL.md`). On Windows the config directory is `%USERPROFILE%\.config\opencode`.

6. Report exactly: `CLIP TOOL READY — installed at <path>`. Then tell the user to
   open a new OpenCode session and run `/clip <url> <start>-<end> [profile]`.

## Notes

- The install is safe to re-run; it does not delete projects or downloads.
- Generated files live in `projects/`, `downloads/` and `.venv/` and are gitignored.
- Whisper's first model download is ~500 MB; it happens during install.
- `earshot doctor` reports sound-tool status. Earshot's listening models download
  on first listening call; to pre-fetch, run `CLIP_TOOL_EARSHOT_FETCH=1 python install.py`.
- The `openverse` skill needs no API key. The `real-sfx` UI sounds are CC0 and
  ship inside the skill; upstream licences are in `.opencode/skills/LICENSE-*.txt`.
