---
name: Clip Tool
description: Install, configure and run the stream-reel clip maker: download an exact YouTube timestamp, transcribe, translate to Roman Hinglish captions, show a storyboard for approval, then render a 1440p60 vertical reel.
---

# Clip Tool

Use this skill whenever the user asks to make a clip/reel from a stream, or to install/update the clip tool.

## Runtime

Read `<config-home>/opencode/clip-tool-path.txt` to find the repository root
(`<config-home>` is `$XDG_CONFIG_HOME` or `~/.config`). Call it `<repo>`.

- Python with all dependencies: `<repo>/.venv/Scripts/python.exe` on Windows, `<repo>/.venv/bin/python` elsewhere.
- Scripts: `<repo>/app/tools/*.py` (always pass `--config <project>/config.json`).
- Rules and full settings: `<repo>/app/docs/CLIP_SETTINGS.md` and `<repo>/app/presets/stream_reel_preset.json`.
- Emoji: `<repo>/app/assets/emoji/<code>.png` (Twemoji hex codes, e.g. `1f681`).
- Meme SFX: `<repo>/app/sfx/meme/<name>.mp3`.

If `clip-tool-path.txt` does not exist, the tool is not installed. Clone the repo and run `python install.py` first.

## Making a clip

### 1. Collect inputs
Ask for (or parse from the request): YouTube URL, start timestamp, end timestamp.
Default caption profile is `full_cue_fade`. If the user wants per-word lighting, use
`karaoke_highlight` — but always confirm the profile before rendering.
Never accept a request to cut, re-time or shorten the clip.

### 2. Create the project
```sh
<python> <repo>/app/tools/new_project.py --url "URL" --start "HH:MM:SS" --end "HH:MM:SS" [--profile karaoke_highlight]
```
Returns the `config.json` path. All later commands use it.

### 3. Download the exact section
```sh
<python> <repo>/app/tools/download.py --config <config>
```
It picks the highest-resolution 60fps format and verifies the duration equals the
requested range. Do not crop the timeline afterwards.

### 4. Confirm the facecam
```sh
<python> <repo>/app/tools/facecam_grid.py --config <config>
```
This prints candidate crops and writes `facecam_grid.jpg` + `facecam_candidates.jpg`
in the project folder. **Preview the grid for the user** (or give them the paths),
ask which crop is the real facecam, then write their choice into `config.json` as
`"facecam_crop": [x0, y0, x1, y1]` (source-video pixel coordinates). The facecam is
NOT always top-left — never skip this confirmation.

### 5. Transcribe
```sh
<python> <repo>/app/tools/transcribe.py --config <config>
```
It runs Whisper `small`, and a forced pass (`no_speech_threshold=0.95`,
`condition_on_previous_text=False`) with timeline merge if speech is missed under
loud game audio. It prints numbered segments.

### 6. Write Roman Hinglish cues — do this yourself
Translate the spoken English into **Roman Hinglish**. Do NOT keep English verbatim.
Write `<project>/caption_cues.json`:

```json
{
  "duration": 63.0,
  "cut": false,
  "language": "roman_hinglish",
  "word_reveal": true,
  "cues": [
    {
      "i": 1,
      "s": 0.00,
      "e": 0.92,
      "text": "CHALO!",
      "words": [{"w": "CHALO!", "t": 0.00}],
      "hl": ["CHALO!"],
      "pop_emoji": "1f3c3",
      "inline_emoji": {"code": "1f4a8", "after": 0}
    }
  ]
}
```

Rules:
- One cue per speech segment. `s`/`e` come from the Whisper segment. **No text during silence.**
- `words` has one entry per word in `text`, with reveal times mapped from Whisper
  word timestamps. Keep `t` inside the cue span and spaced at least 0.12s apart.
- `hl` lists the words shown in red. `pop_emoji` is the big emoji after the first word.
- `inline_emoji` is inserted between dense-line words; `after` is a word index.
- Missing emoji? Download `https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/<code>.png`
  into `<repo>/app/assets/emoji/<code>.png`.

### 7. Storyboard → approval (mandatory)
```sh
<python> <repo>/app/tools/storyboard.py --config <config>
```
Preview `storyboard.jpg` for the user and ask for approval before rendering. Confirm
the caption profile again if they did not choose one earlier.

### 8. SFX events
Add 2–4 sparse meme hits at genuinely crazy moments to `config.json`:
```json
"sfx_events": [
  {"t": 21.08, "name": "vine_boom", "gain": 0.55},
  {"t": 43.64, "name": "metal_gear_alert", "gain": 0.45}
]
```
Available names are the `.mp3` filenames in `<repo>/app/sfx/meme`. No beat song,
no music bed. Voice is normalized; SFX sit under it.

For extra sounds, use the bundled skills (installed beside this one):
- `openverse` — free CC-licensed recorded sounds, no API key; writes `CREDITS.md`.
  `python <config-home>/opencode/skills/openverse/scripts/openverse.py search "whoosh" --license cc0`
- `earshot` — make a new SFX from words: `earshot make "cartoon boing" -o sfx.wav`.
  Its `describe`/`compare` commands can verify audio you cannot hear.
- `real-sfx` / `real-sound` — place real recordings on exact frames, or source,
  license and mix a soundtrack.

Still no beat song: extra sounds are sparse one-shots at crazy moments only.

### 9. Render
```sh
<python> <repo>/app/tools/render.py --config <config>
```
This produces the final MP4 in `<repo>/downloads` and saves its path in
`config.json` as `final`.

### 10. Verify and show
```sh
<python> <repo>/app/tools/verify.py --config <config>
```
It checks 1440x2560/60fps, exact duration, H.264/AAC, caption presence on speech,
blank frames during silence. Then preview the final MP4 for the user.

## Hard rules
- Output duration must exactly equal the requested timestamp range.
- Never use `word_by_word_reveal` (deprecated: sync gaps and missing text).
- RGB→BGR: PIL overlays are RGB, cv2 frames are BGR; composite in RGB, convert back.
- Show the storyboard and get approval before every render.
- Captions are Roman Hinglish translations, never English verbatim.
