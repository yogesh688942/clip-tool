# Clip-Making Settings — Complete Saved Recipe

This is the **master settings file** for making a reel from a supplied YouTube timestamp.
It lives on disk, so it survives clearing the chat or starting a new OpenCode session.
Also kept in sync in `style-sheet.md` (Section 9), `README-tools.md`,
`presets/stream_reel_preset.json`, and in the shareable installer repo
`clip-tool/app/docs/` + `clip-tool/app/presets/`.
Last updated 2026-11-24.

---

## 1. Source and download

- Current stream: `https://www.youtube.com/live/iyxP3wCTtP4?si=K5UBE-qe35axqABD`
- Check available formats first: `yt-dlp -F "URL"`
- Download the exact section (never re-time afterwards):

```powershell
yt-dlp --no-playlist --download-sections "*02:23:17-02:23:40" --force-keyframes-at-cuts -f "623+234/308+251/bestvideo+bestaudio" --merge-output-format mp4 -o "downloads\stream_02-23-17_02-23-40.%(ext)s" "URL"
```

- **NEVER cut, re-time or shorten the clip.** Output duration = requested timestamp difference exactly.
- Use the highest resolution available at 60 fps. This stream: `2560×1440 / 60 fps` source. If `2160p60` is offered, use it instead.

## 2. Canvas and encode

| Setting | Value |
| --- | --- |
| Output | **1440×2560**, vertical 9:16, **60 fps** |
| Video | H.264 (`libx264`, `veryfast`, `crf 17`, `yuv420p`, `+faststart`) |
| Audio | AAC, 192 kbps |
| Duration | Exact requested length (e.g. 23.000 s) |
| Upgrade rule | 2160×3840 / 60 fps if the source offers 2160p60 |

## 3. Layout

- Split line: **y = 1093** in the 1440×2560 output.
- **Upper panel (y 0–1093): facecam**, detected per clip and confirmed by the user with a labeled grid preview before the storyboard.
  - Top-left duo stream crop: `[0, 467, 667, 973]`
  - Tight left facecam crop: `[180, 720, 500, 1010]` ← used for the current 31 s clip
  - Top-right duo stream crop: `[1980, 0, 2560, 440]`
  - Lower-right facecam crop: `(1950, 930, 2400, 1330)` ← used for the 63 s and 56 s clips
  - Crop is resized edge-to-edge to 1440×1093 (no black bars); faces centered, wider view.
- **Lower panel (y 1093–2560): gameplay**, tight center crop: resize source to 2608×1467, then take x 584–2024.
- No watermark, no annotation strips, no divider.

## 4. Captions

- Font: `tools/fonts/Montserrat-Variable.ttf`, weight 800; renderer scale = `output_width/1080` (4/3 at 1440 wide).
- Sizes: pop ≈ 107 px (80×4/3), dense ≈ 64 px (48×4/3); line spacing 54×scale; strokes pop 12, dense 9.
- Colors: dense mint `#1EE3B2`, highlight red `#FF3B30`, pop yellow `#FFD400`, outline black.
- Language: **Roman Hinglish** — translate the spoken English into Hinglish. Do not keep English verbatim.
- One cue at a time. No text at all during silence.
- Emoji on every cue: 88 px color emoji right of the yellow pop word; 44 px inline between dense-line words. Twemoji 14.0.2 PNGs in `assets\emoji\`.

### Display profiles

| Profile | Status | Behavior |
| --- | --- | --- |
| `full_cue_fade` | **Default** | Whole cue shown at once, fade in/out 0.10 s. |
| `karaoke_highlight` | Optional (chosen for recent clips) | Whole cue visible from cue start in a dimmed state; each word eases up to full brightness in sequence. Dim factor 0.50 + floor 25, smoothstep easing over 0.18 s per item, cue fade 0.10 s. Never loses text mid-sentence. Used for the 23 s, 63 s and 56 s reels. |
| `word_by_word_reveal` | **Deprecated — do not use** | Per-word fade-in caused sync gaps and missing text while the person was speaking. |

Reference implementations:
- Default full-cue: `projects\stream_02-23-17\render_full.py` + `emoji_text.py`
- Karaoke: `projects\stream_02-23-17\render_karaoke.py` + `karaoke_caption.py`
- Deprecated reveal: `projects\stream_02-23-17\render.py` + `word_caption.py`

> Compositing rule: PIL overlays are **RGB**, cv2 frames are **BGR** — always convert the frame to RGB, composite, then convert back. (A past render swapped these and turned yellow/red captions into cyan/blue.)

## 5. Audio

- **No beat song, no music bed.**
- Voice: `loudnorm=I=-14:TP=-1.5:LRA=11`; SFX mixed at 0.85 under the voice.
- SFX source: MyInstants (`https://www.myinstants.com/en/search/?name=Meme`).
- Fetch `https://www.myinstants.com/en/instant/<slug>/`, take the first `/media/sounds/*.mp3` link, download with a browser User-Agent, trim to ~1–2 s.
- Placement: sparse — only at genuinely crazy moments.
- Past 23 s events: `0.00 oh_my_god`, `7.12 vine_boom`, `21.40 bruh`.
- Current 31 s events: `15.66 metal_gear_alert`, `22.76 oh_my_god`, `26.48 bruh`.

## 6. Transcription and cue building

- `whisper` model `small`, `language="en"`, `word_timestamps=True`.
- If Whisper finds too little speech under loud game audio, re-run with `no_speech_threshold=0.95`, `condition_on_previous_text=False`; merge word timelines and discard garbled fragments.
- Build `caption_cues.json` per project: `s`, `e`, `text`, per-word times, `hl` highlight words, `pop_emoji`, `inline_emoji`.

## 7. Workflow

1. Download the exact timestamp; verify with `ffprobe` (resolution, 60 fps, exact duration).
2. Detect facecam, confirm position with the user via a labeled grid preview.
3. Transcribe (normal pass; forced pass only if needed).
4. Build Hinglish cues and a **storyboard** — always show it for approval before rendering.
5. Fetch meme SFX and build `audio.m4a`.
6. Render with the chosen caption profile.
7. Verify: `ffprobe` specs, caption present on speech frames, blank during silence, (for karaoke) brightness increases through each cue.
8. Open the final video in the Review pane.

## 8. Current projects

| Project | Source span | Output | Caption profile |
| --- | --- | --- | --- |
| `stream_02-18-49` | 02:18:49–02:20:00 (71 s) | `reel_02-18-49_1440p60_hinglish_word_by_word.mp4` | deprecated reveal (left as-is) |
| `stream_02-23-17` | 02:23:17–02:23:40 (23 s) | `reel_02-23-17_1440p60_hinglish_karaoke.mp4` | `karaoke_highlight` |
| `stream_02-23-17` | same | `reel_02-23-17_1440p60_hinglish.mp4` | `full_cue_fade` |
| `stream_01-58-27` | 01:58:27–01:59:30 (63 s) | `reel_01-58-27_1440p60_hinglish_karaoke.mp4` | `karaoke_highlight` |
| `stream_03-16-03` | 03:16:03–03:16:59 (56 s) | `reel_03-16-03_1440p60_hinglish_karaoke.mp4` | `karaoke_highlight` |
| `stream_04-52-44` | 04:52:44–04:53:15 (31 s) | `reel_04-52-44_1440p60_hinglish.mp4` | `full_cue_fade` |

Older files in `downloads\` (`*_word_by_word.mp4`) are superseded and can be deleted.
