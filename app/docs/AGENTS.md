# Project instructions — AI Video Editor

Before making any clip or editing clip settings, read `CLIP_SETTINGS.md` in this
folder. It is the master saved recipe and survives clearing the chat or starting
a new session. Also available: `style-sheet.md` Section 9, `README-tools.md`,
and `presets/stream_reel_preset.json`.

## Non-negotiable rules

- Never cut, re-time or shorten a supplied clip. Output duration must exactly
  equal the requested timestamp range.
- Default output: 1440×2560 / 60 fps. Use the highest 60fps resolution the source
  offers; upgrade to 2160×3840 if 2160p60 is available.
- Detect the facecam per clip and confirm the crop with the user via a labeled
  grid before building the storyboard. It is not always top-left.
- Captions are Roman Hinglish translations of spoken English — never English
  verbatim. One cue at a time, no text during silence.
- Saved caption profiles: `full_cue_fade` (default), `karaoke_highlight`
  (optional, chosen for recent clips), `word_by_word_reveal` (deprecated — do not use).
- If Whisper misses speech under loud game audio, re-run with
  `no_speech_threshold=0.95`, `condition_on_previous_text=False`, merge word
  timelines and discard garbled fragments.
- No beat song. Voice + sparse MyInstants meme SFX at crazy moments only.
- Always show the storyboard and get approval before rendering.
- PIL overlays are RGB and cv2 frames are BGR: composite in RGB, convert back.
- After finishing a clip, add it to the project table in `CLIP_SETTINGS.md`
  and to `presets/stream_reel_preset.json`, then verify with `ffprobe`.

The shareable one-click installer lives in `clip-tool/`. Keep its
`app/docs/` and `app/presets/` copies in sync with the files in this folder.
