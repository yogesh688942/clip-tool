# Clip Tool — one-click install through OpenCode

A complete, self-contained stream-reel maker. It downloads an exact YouTube
timestamp, detects the facecam, translates speech into Roman Hinglish captions,
shows a storyboard for approval, then renders a vertical 1440p60 reel with
sparse meme SFX and no beat.

## Install on another computer (the shareable link)

1. Install OpenCode (one command): <https://opencode.ai/docs/>
2. Open OpenCode in any empty folder.
3. Paste this single line and press Enter:

```
Install the clip tool from https://github.com/yogesh688942/clip-tool.git by cloning it into ~/clip-tool (or Documents\clip-tool on Windows), then run `python install.py` inside the cloned repo. Follow INSTALL.md exactly. Confirm with "CLIP TOOL READY" when done.
```

OpenCode clones the repo, creates a virtualenv, installs Python/ffmpeg dependencies
and the sound tools, pre-downloads Whisper, and registers global OpenCode skills
plus a `/clip` command. The whole install is automatic.

The install needs `git` (to fetch Earshot) and downloads about 1.5 GB the first
time: Whisper (~500 MB), CPU PyTorch + Earshot, plus the listening models
(~1.1 GB) on first use. Set `CLIP_TOOL_EARSHOT_FETCH=1` before running
`python install.py` to fetch those models during install instead.

## Make a clip

In OpenCode, paste:

```
/clip https://www.youtube.com/live/VIDEO_ID?si=... 01:58:27-01:59:30 karaoke_highlight
```

or in plain language:

```
Make a clip from URL starting 1:58:27 ending 1:59:30 using karaoke highlight captions.
```

OpenCode will:
1. download only that exact range (no cuts or re-timing),
2. show a labeled grid so you can confirm the facecam crop,
3. transcribe and write Roman Hinglish cues,
4. show a storyboard and ask for approval,
5. render, verify, and open the final MP4.

## Caption profiles

| Profile | Behavior |
| --- | --- |
| `full_cue_fade` | Saved default. Whole cue appears at once, 0.10s fades. |
| `karaoke_highlight` | Whole cue dimmed, each word eases to full brightness at its word time. |
| `word_by_word_reveal` | Deprecated — do not use. |

## What is included

- `app/tools/` — download, transcribe, facecam detection, storyboard, render, audio, verify
- `app/lib/` — caption + emoji renderers
- `app/presets/` — machine-readable locked preset
- `app/docs/` — full saved settings and style sheet
- `app/assets/` — Twemoji PNGs and Montserrat font
- `app/sfx/meme/` — MyInstants meme sounds
- `.opencode/` — installable global skills and `/clip` command

## Sound tools (bundled)

- **openverse** — search and download free CC-licensed recorded sounds from the
  public Openverse API. No API key. Writes attribution automatically.
- **real-sfx** — sound-design a video from real recordings placed on exact frames;
  ships 78 CC0 UI cues.
- **real-sound** — source, license, mix, master and credit real audio for a film.
- **earshot** — make SFX from plain English on CPU, and "listen" to audio to
  describe, compare and verify it.

All four are copied into `~/.config/opencode/skills` by `install.py`. The bundle
keeps the upstream licences in `.opencode/skills/LICENSE-*.txt`.

See `INSTALL.md` for the exact installer steps and `CLIP_SETTINGS.md` in `app/docs/`
for the complete locked recipe.
