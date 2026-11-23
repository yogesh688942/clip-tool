# AI Video Editor — toolkit quick reference

All tools are free. Work from this folder (`D:\AI Video Editor`).

## LOCKED DEFAULT EDIT RECIPE — use for every clip

The user confirmed this is the only style to use from now on. Read these before any edit:

- `style-sheet.md` → **Section 9: Approved production preset** (authoritative, human-readable)
- `CLIP_SETTINGS.md` → **complete saved settings** for making clips (source/download, encode, layout, captions + profiles, audio, transcription, workflow)
- `presets\stream_reel_preset.json` → same settings, machine-readable (includes `caption_profiles` and `project_examples`)
- `projects\stream_01-06-30\emoji_text.py` → caption + emoji renderer
- `assets\emoji\` → downloaded Twemoji PNGs (fetch more from `https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/<code>.png`)
- `projects\stream_01-55-34\render.py` → working reference implementation (1440p60)
- `projects\stream_01-55-34\storyboard.py`, `make_cues.py`, `transcribe_words.py` → reference workflow scripts for a new clip

Key rules: **never cut or shorten the supplied clip** (output = exact timestamp length, full continuous timeline); **1440×2560/60fps default — use the highest resolution available at 60fps (upgrade to 2160p60/4K when offered)**; coordinates in the preset are a 1080×1920 base space scaled by `output_width/1080`; **detect the facecam per clip** (face detection + labeled grid confirmation — top-left in some streams, top-right in others), frame it wider and centered in the top y 0–820 panel, tight gameplay bottom y 820–1920; captions in Roman Hinglish (translate the spoken English) only while speech is present, one cue at a time with **0.10 s fades** — show the **whole cue at once, NO word-by-word reveal** (word-by-word was reverted: it fell out of sync with the speaker and left frames with no text while they were talking); emoji fade with the whole cue (**if Whisper finds too little speech, re-run with `no_speech_threshold=0.95` — loud game audio can hide dialogue**); **no beat song / no music bed** — voice + sparse meme SFX at only the genuinely crazy moments, sourced from MyInstants (`https://www.myinstants.com/en/search/?name=Meme`; get the MP3 from the instant page's first `/media/sounds/*.mp3` link) and trimmed to ~1–2 s, voice stays on top; **always show a storyboard for approval before rendering**.

## Folder layout

| Folder | What goes there |
| --- | --- |
| `downloads\` | Videos fetched with yt-dlp |
| `clips\` | Trimmed segments made with FFmpeg |
| `captions\` | Whisper transcripts / `.srt` caption files |
| `tools\` | HyperFrames installer and app |

## 1. Download reels — yt-dlp

```powershell
yt-dlp -f "bv*[height<=1080]+ba/b" -o "downloads\%(title)s [%(id)s].%(ext)s" "PASTE_URL_HERE"
```

- It automatically merges the best video + audio using the installed FFmpeg.
- For a short clip only: `yt-dlp --download-sections "*00:00:10-00:00:25" -o "downloads\part.%(ext)s" "URL"`

## 2. Cut and trim — FFmpeg

Fast cut (no re-encoding, starts at the nearest keyframe):

```powershell
ffmpeg -ss 00:00:10 -i "downloads\input.mp4" -t 15 -c copy -avoid_negative_ts make_zero "clips\clip.mp4"
```

Frame-accurate cut (re-encodes):

```powershell
ffmpeg -ss 00:00:10 -i "downloads\input.mp4" -t 15 -c:v libx264 -crf 18 -preset fast -c:a aac "clips\clip.mp4"
```

## 3. Word-by-word captions — Whisper

Using the included helper (writes one SRT entry per word):

```powershell
python captions\word_captions.py "clips\clip.mp4"
python captions\word_captions.py "clips\clip.mp4" --model medium --language en
```

Models, fastest to most accurate: `tiny`, `base`, `small`, `medium`, `large`.
The first run downloads the model weights. CPU transcription is slower than a GPU.

Plain CLI alternative (segment-level captions):

```powershell
whisper "clips\clip.mp4" --model small --word_timestamps True --output_format srt --output_dir captions
```

## 4. Motion graphics — HyperFrames

- Installed app: `%LOCALAPPDATA%\Programs\HyperFrames\HyperFrames.exe` (official free HeyGen app). Installer copy kept at `tools\Install-HyperFrames.exe`. Sign in with a free HeyGen account at first launch.
- Projects are saved in `%USERPROFILE%\.hyperframes-studio`, exports go to your Downloads folder.
- Command-line alternative (needs Node.js 22+, already installed):

```powershell
npx hyperframes init my-video
cd my-video
npx hyperframes preview
npx hyperframes render
```

## Verify installations

```powershell
ffmpeg -version
yt-dlp --version
whisper --help
```
