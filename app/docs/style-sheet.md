# Default Style Sheet — Short-Form Reels

> **LOCKED DEFAULT:** For every new clip, use **Section 9 — Approved production preset** below. It is the user-confirmed recipe (no cuts, full timestamp, speech-timed emoji **Hinglish** captions shown as full cues with **0.10 s fades**, wider centered facecam, **voice + sparse meme SFX — no beat song**). **Resolution: 1440×2560 / 60 fps by default — use the highest resolution available at 60 fps (upgrade to 2160p60 when the source offers it).** Machine-readable copy: `presets\stream_reel_preset.json`. Sections 1–8 remain the measured reference analysis only.

**Applies to every edit in this workspace.** Derived from the four supplied reference reels (1080×1920, 60 fps, 12.6–23.5 s) using frame sampling, OCR, color sampling, scene-change detection, and SIFT zoom analysis. Measured values are labelled; where the sources could not supply a value (they contain **no audio stream**), the value below is the mandatory house default.

## 0. Source analysis summary

| Reel | Duration | Cuts | Avg shot | Visual changes | Accent | Dense glyph | Pop glyph | Median zoom |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCOUT_ROASTED… | 12.62 s | 7 | 1.58 s | every 0.48 s | mint `#1EE3B2` (measured) | 48–54 px | 72–120 px | 1.003× (static) |
| short 2 | 14.52 s | 6 | 2.08 s | every 0.81 s | cyan `#00E3FB` (measured) | 38–44 px | 62–110 px | 1.012× (static) |
| short 3 | 23.45 s | 1 | 11.7 s | every 2.13 s | mint `#1BEBB7` (measured) | 39–48 px | 60–112 px | 1.031× (punch-ins to 1.30×) |
| short 4 | 18.78 s | 9 | 1.88 s | every 0.69 s | mint `#19EBB6` (measured) | 48–67 px | 64–101 px | 1.010× (static) |

No persistent split-screen was detected in any reel (vertical-seam metric 9.6–13.3; a real split would exceed ~25).

---

## 1. Fonts and typography

**Font file:** `D:\AI Video Editor\tools\fonts\Montserrat-Variable.ttf` (variable font — set the weight axis to **800**). Fallback: `impact.ttf` from `C:\Windows\Fonts` at the same pixel sizes.

| Element | Font | Size | Weight | Color | Notes |
| --- | --- | --- | --- | --- | --- |
| Dense caption (1–2 lines) | Montserrat ExtraBold | **64 px** | 800 | `#1EE3B2` mint (default) / `#00E3FB` cyan (alternate) | Line height 68 px; letter spacing −1 px; centered |
| Single-word pop | Montserrat ExtraBold | **112 px** | 800 | `#FFFFFF` | Up to 160 px for the single biggest hook word |
| Emphasis word inside a dense line | Montserrat ExtraBold | same as parent | 800 | `#FFFFFF` (inverts against accent line) | 0.18 s flash, then back to accent; max 1 word per line |
| Handle / watermark | Montserrat Bold | **52 px** | 700 | Same accent as the caption, 90% opacity | Centered just above the caption block |
| Outline (all text) | — | **6 px** dense / **10 px** pop | — | `#000000` | Hard outline, no shadow blur |
| Drop shadow | — | offset (0, 4) px, blur 0 | — | `#000000` at 60% | Only on pop words |

**Why these sizes:** measured dense glyph heights are 38–67 px (median ≈ 46 px) and pop glyph heights are 60–120 px (median ≈ 78 px). With a ~0.70 cap-height ratio this gives ≈ 63 px and ≈ 112 px respectively. The earlier 80 px / 150 px estimates were too large and are superseded.

**Caption position:** center of the dense block at **y = 1000 px** by default (measured centers: 1020 scout, 1028 short 2, 996 short 3, 938 short 4 — acceptable range 938–1030). In the 2-line case line 1 sits ≈ y 950–1010 and line 2 ≈ y 1020–1090 (scout). In the 1-line case the line sits ≈ y 878–1063 depending on the reel. Horizontal span ≈ 760 px, centered → x ≈ 160–920 px (side margin ≈ 160 px). The handle sits 60–90 px above the dense block (y ≈ 813–965 px measured). Single-word pops sit at y ≈ 731–975 px (center ≈ 795–901). Do not add graphic text below y = 1200 px — short 4 carries a source-footage promo banner at y ≈ 1700–1914 that is **not** part of the house style.

**How words appear:** each dense line pops in over **0.15–0.20 s** with an ease-out-back curve (overshoot 1.08), holds 0.6–1.0 s, and exits in 0.10 s (ease-in). Pop words appear one at a time, roughly **one every 0.8–1.0 s** — measured exactly one pop per second from 2.0 s to 20.0 s in short 3, and ~0.8–1.0 s spacing in short 2. No typewriter effect, no per-letter delay within a word.

---

## 2. Colors and grading

| Token | Hex | Use |
| --- | --- | --- |
| Ink / shadow | `#040105` | Deepest black, letterbox-free background |
| Near-black warm | `#25201D` | Shadow lift |
| Neutral dark | `#1D1917` | Mid-shadow |
| Warm mid | `#4D3E2F` | Skin/interior mids |
| Cool mid | `#64686F` | Blue-gray mids |
| Light neutral | `#CAB7B0` | Highlight roll-off |
| Mint accent | `#1EE3B2` | **Primary dense-caption fill** (measured scout) |
| Cyan accent | `#00E3FB` | **Alternate dense-caption fill** (measured short 2) |
| Blue accent | `#6BCEF1` | Supporting graphics only (not caption text) |
| Yellow accent | `#F8D910` | Secondary punchline highlight |
| White | `#FFFFFF` | Single-word pops, inline emphasis flash |

**Rule:** the dense caption block is **filled with the accent color**, not white. The white is reserved for the separate large word pops and for a brief inline emphasis inversion. The handle/watermark uses the same accent as the caption (measured `#21E5B4` mint in scout, `#00E1F7` cyan in short 2, `#1AEAB6` mint in short 3, `#1CEAB6` mint in short 4). All four reels use a green-cyan accent family; measured dense fills cluster at `#18EBB6`–`#1EE3B2` with short 2 as the bluer outlier at `#00E3FB`.

**Grade target:** mean luminance L* ≈ 95 (acceptable 58–127 across refs), contrast σ(L*) ≈ 60 (54–68), mean saturation ≈ 85 (67–101), color temperature R−B ≈ +12 (range 0.6–25.2). Apply a gentle vignette: center ≈ +30 L* brighter than corners. Keep highlights below 95% and crush nothing below 3%. Prefer warm mids with cool shadows; no teal-orange blockbuster look.

---

## 3. Layout

- Full-bleed 1080×1920 source footage. No letterbox, no pillarbox, **no split screens**.
- Two recurring text layouts, used alternately:
  1. **Dense commentary block** — **1 or 2 centered lines**, **7–11 words per line** (measured: scout 10–11 words/line over 2 lines; short 2 exactly 7 words in 1 line), x ≈ 160–920, y ≈ 878–1090 (default center ≈ 1000), accent-colored.
  2. **Single-word pop** — one white word, 112 px, centered at y ≈ 731–975 (default ≈ 900), used for punchlines/emphasis; roughly one per 0.8–1.0 s.
- Small accent-colored handle/watermark sits immediately above the dense block (measured y ≈ 813–965 px, 60–90 px above the caption).
- B-roll = hard-cut source shots; no picture-in-picture, no persistent panels.
- Camera is **static by default**. Keep punch-ins rare (1–2 per reel): 1.00 → 1.06× in 0.35 s ease-out cubic, returning to 1.00× on the next cut. Measured medians were 1.003×, 1.012× and 1.010× for scout, short 2 and short 4. Exception: for a long single-location reel (short 3), use continuous slow zooms and punch-ins up to **1.30×** (measured 29 zoom-in events, p90 = 1.153×).

---

## 4. Motion

| Parameter | Value |
| --- | --- |
| Cut type | Hard cut only (no dissolves, no fades except final 0.2 s fade-out) |
| Cut times in hook | 0.05 s, 0.80 s, 2.00 s |
| Average shot length | 1.8 s (refs: 1.58, 2.08, 11.7, 1.88) |
| Visual change interval | 0.6 s (refs: 0.48, 0.81, 2.13, 0.69) |
| Word pop-in | 0.18 s, ease-out-back (overshoot 1.08) |
| Emphasis flash | 0.18 s white flash at pop onset, reverting to accent when the 0.18 s pop-in completes |
| Word exit | 0.10 s, ease-in |
| Punch-in zoom | 1.00 → 1.06× in 0.35 s, ease-out cubic (up to 1.30× for long single-shot reels) |
| Transition into next shot | Cut on the beat; SFX lands on the same frame (±1 frame) |

---

## 5. Captions

- Style: Montserrat ExtraBold **64 px**, **accent fill** (`#1EE3B2` default, `#00E3FB` alternate), 6 px black outline, centered, sentence case.
- **Words per line:** 7–11 in dense mode; 1 in pop mode. Never more than 2 lines.
- Dense lines are already accent-colored; deliver emphasis either by (a) replacing the line with a single **white 112 px word pop** (preferred, matches all four measured reels), or (b) a 0.18 s white inversion of one word inside the line.
- Accent choice: mint `#1EE3B2` for the primary commentary reel, cyan `#00E3FB` for a brighter/lighter look; keep one accent per edit, with yellow `#F8D910` reserved for a single punchline.
- Captions are on screen ~92–93% of the time (measured); keep gaps under 0.25 s.
- Do not cover the subject's face; if needed, shift the whole block up by at most 60 px.

---

## 6. Sound design

**Important:** the four supplied reference files contain **no audio streams** (verified with ffprobe). Therefore no music/SFX could be measured from them. The values below are the **mandatory house defaults** for all future edits.

| Element | Spec |
| --- | --- |
| Music | Hype/trap or desi-fusion instrumental, 96–108 BPM, -20 LUFS integrated |
| Voice | -14 LUFS integrated, -1 dBTP ceiling; duck music 6 dB while voice is present |
| Music ducking | 0.15 s attack, 0.35 s release |
| Whoosh | 0.18 s, filter sweep 400 Hz → 6 kHz, peak -8 dBFS, starts 1 frame before each hard cut |
| Pop / click | 0.06 s, 1.2 kHz blip, peak -10 dBFS, exactly on each word-pop onset |
| Sub hit | 0.25 s, 60 Hz, peak -6 dBFS, on the hook word at 0.00 s and on major punchlines |
| Rise | 0.60 s white-noise riser into the 2.00 s hook cut, peak -12 dBFS |
| Silence | Never more than 0.20 s of dead air |

---

## 7. Pacing and hook

- Target total length 12–20 s.
- Average shot 1.8 s; visual change every 0.6 s.
- **First 3 seconds (hook):**
  - 0.00–0.10 s: first hard cut + subject/meme visible immediately.
  - 0.18 s: first dense caption line fully popped in (0.18 s pop-in).
  - 0.80 s: second cut (measured in reels 1 and 2).
  - 2.00 s: third cut or context shot (measured in reel 1).
  - 2.00–3.00 s: first large white word pop to lock attention (measured: `"kya"` at 8 s in scout and `"bhai"` at 2 s in short 2 — move the first pop into the hook in new edits).
- Never open with a logo or title card.

---

## 8. Verification before export

1. Canvas 1080×1920, 60 fps, H.264, AAC if audio is added.
2. Dense block center y ≈ 1000 px; handle 60–90 px above it; no added text below y = 1200 px.
3. Dense captions use one accent fill (`#1EE3B2` or `#00E3FB`); white is only for word pops / emphasis flashes; handle matches the accent.
4. Dense font 64 px, pop font 112 px, Montserrat weight 800 from `D:\AI Video Editor\tools\fonts\Montserrat-Variable.ttf`.
5. At least one hard cut at 0.05–0.10 s and a second by 0.80 s in the first 3 s.
6. Zoom stays at 1.00–1.06× unless the reel is a long single-location shot.
7. Music -20 LUFS, voice -14 LUFS, SFX on cut frames.

---

## 9. Approved production preset (stream-clip reels) — USE THIS BY DEFAULT

Confirmed 2026-11-21 and **locked as the permanent default on 2026-11-22** ("save all settings for every time I make a clip — make like this only"). Built on the `l-oEKLu4Y3w` stream segment. **For every future clip, this preset overrides the conflicting reference defaults in sections 1–8 above** (those remain the measured reference analysis, this is the user-approved house build). No re-approval of these settings is needed — only the storyboard for each new clip still needs approval.

### Timeline (most important — do not cut the user's clip)
- **NEVER cut, re-time, or shorten a clip the user supplies.** If they give a 40-second timestamp, the output is the **full 40 seconds** in one continuous pass. The earlier 9-shot / 16.2 s cut reel was rejected for this reason.
- Do not add shots, drop shots, reorder moments, or apply `atempo` to the source. Output duration must equal the requested timestamp length exactly.

### Resolution policy (updated 2026-11-22)
- **Default output: 1440×2560, 60 fps** (vertical 9:16). H.264 CRF 17 + AAC 192k.
- **Use the highest resolution the source offers at 60 fps.** If 2160p60 / 4K is available, render 2160×3840 instead of 1440×2560. Always check `yt-dlp -F` for the best 60 fps format before downloading.
- All layout/caption numbers below are in a **1080×1920 base space** — multiply every coordinate by `output_width / 1080` (e.g. ×4/3 for 1440p, ×2 for 2160p). Source crop numbers are in a **1920×1080 base space** — multiply by `source_width / 1920`.
- Verified 1440p build: 2560×1440 source → facecam crop `(0, 467, 667, 973)`, split y 1093, gameplay crop x 584–2024, caption renderer scale 4/3.

### Canvas and layout (1080×1920 base space)
- 1080×1920 base (= 1440×2560 at default), 60 fps, H.264 + AAC. Duration = full requested timestamp.
- **Facecam top panel (y 0–820), tight gameplay centre crop bottom panel (y 820–1920).** No blurred background, no letterbox, no watermark/handle, no black annotation strips.
- Facecam: **slightly smaller, wider view, face centred** — source crop `(0, 350, 500, 730)` = 500×380 (at 1920×1080 source), enlarged to the top panel. (The earlier tight 320×280 crop was rejected as too zoomed.) Tight gameplay: scale the full source frame so its height equals the bottom panel, then centre-crop to output width.
- **Locate the facecam per clip — never assume top-left.** Run face detection on several frames of the new source, find the consistent face cluster(s), frame them centred with a wider view, and confirm the position with the user using a labeled grid preview before building the storyboard. Verified examples: top-left stream `(0,467,667,973)`; top-right duo stream `(1980,0,2560,440)` (both faces at x≈2205 and x≈2455, y≈165).
- **Text sits directly on the split line**: yellow word-pop just above (centre y ≈ 775), dense caption just below (line 1 y ≈ 865, line 2 y ≈ 919). Heavy black outline (12 px pop / 9 px dense), no text background box, no divider line.

### Typography and language
- Montserrat ExtraBold weight 800 from `D:\AI Video Editor\tools\fonts\Montserrat-Variable.ttf`; pop 80 px, dense 48 px.
- **Default caption language: conversational Roman Hindi (WhatsApp-style Hinglish)**, e.g. `"ITNA TEZ THA."`, `"HONEY FM INDIAN SONG KE LIYE."`, `"TUM MERI BAAT KAT RAHE HO."` Keep proper nouns (Honey FM, PTC Punjab, Sidhu Moosewala, Rinky & Papa) in Roman script.
- **Translate the spoken dialogue into Roman Hinglish** (e.g. `RUN!` → `BHAGO! BHAGO! BHAGO!`, `Brother, they have taken my car's tires out` → `BHAI, MERI CAR KE TYRE NIKAL DIYE.`, `Get out, Jason!` → `JASON, BAHAR NIKAL!`). An earlier "keep English verbatim" rule was tried and reverted on the user's instruction — do not apply it.
- **Colours:** dense caption mint `#1EE3B2` with key words in red `#FF3B30`; word-pop yellow `#FFD400`. No white pops, no handle text.

### Caption timing (word-synced)
- **Captions appear only while the person is actually speaking.** Transcribe with Whisper and use the real segment-level word timings to build cue spans. If the person is silent, show **no text at all** — never fill gaps with captions from other moments.
- **Loud game audio can hide speech from the default Whisper pass.** If the transcript looks implausibly short, re-run with `no_speech_threshold=0.95` and `condition_on_previous_text=False` on the silent stretch, then merge the two word timelines (dedupe overlaps). Verified on the 46 s clip: default pass found only the last 15 s; forced pass recovered 0–32 s of dialogue. Discard hallucinated/garbled fragments.
- **One cue at a time** — never show multiple captions or word-pops simultaneously. Each cue fades in/out over **0.10 s** at its exact speech timing; cues do not overlap. No text appears during silence.
- **Show the whole cue at once — NO word-by-word reveal.** Word-by-word reveal was tried and reverted: per-word timing fell out of sync with the speaker and left frames with no text while the person was still talking. Display the complete caption for the entire cue span; only fade the whole cue in/out over 0.10 s.
- Each cue = one yellow pop (first/keyword word) + one mint/red dense line (max 2 lines), centred on the split line.
- **Emoji on every cue:** one larger color emoji (88 px) immediately to the right of the yellow pop word, plus one smaller color emoji (44 px) **inline between the words** of the dense line. Emoji fade in/out with the whole cue (same 0.10 s transition).
- Emoji assets: Twemoji 14.0.2 PNGs at `D:\AI Video Editor\assets\emoji\` (downloaded via `https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/<code>.png`). Download more there whenever a new emoji is needed. Helper: `projects\stream_01-06-30\emoji_text.py`.
- Silence gaps in the current 40 s clip: 1.00–1.48, 1.98–2.74, 4.52–4.84, 5.38–5.90, 8.30–8.94, 9.94–10.32, 11.22–11.90, 12.66–13.84, 15.92–16.72, 19.30–25.12, 25.80–25.96, 29.64–31.82, 32.76–34.14, 35.82–36.90, 37.44–40.00. Cue data: `projects\stream_01-06-30\caption_cues.json`.

### Caption display profiles (saved 2026-11-22)
- **Default — `full_cue_fade`:** whole cue shown at once, fade in/out 0.10 s. See `projects\stream_02-23-17\render_full.py` + `emoji_text.py`.
- **Optional — `karaoke_highlight`:** the complete caption is visible from cue start in a dimmed state (RGB ×0.50 + 25 floor); each word/pop/inline emoji eases up to full brightness in sequence with smoothstep over **0.18 s** at its word time; cue fades over 0.10 s. Text never disappears mid-sentence. Used for the 23 s, 63 s and 56 s reels; see `projects\stream_02-23-17\render_karaoke.py` + `karaoke_caption.py`.
- **Deprecated — `word_by_word_reveal`:** do NOT use. Per-word fade-in caused sync gaps and missing text while the person was speaking.
- Compositing: PIL overlays are RGB, cv2 frames are BGR — convert frame to RGB, composite, then convert back.
- Full machine-readable settings: `presets\stream_reel_preset.json` (`caption_profiles`) and `CLIP_SETTINGS.md`.

### Sound design
- **No beat song / no music bed.** This supersedes the old 120 BPM beat rule — do not add any background music.
- Voice: −14 LUFS, −1.5 dBTP, `loudnorm=I=-14:TP=-1.5:LRA=11`.
- **Meme SFX only at the genuinely crazy moments** (screams, "OH NO!", frustration, the chaotic peak). Keep it sparse — a handful of hits, not a constant layer. Voice always stays clearly on top. Old synthesized whoosh/boom/beep/scratch/sting packs are retired.
- Source SFX from **MyInstants** (user-specified): `https://www.myinstants.com/en/search/?name=Meme`. To get a sound's real MP3, fetch its `https://www.myinstants.com/en/instant/<slug>/` page and pull the first `/media/sounds/*.mp3` link; download with a browser User-Agent. Verified working picks: `oh_my_god`, `chicken_scream`, `vine_boom`, `nuagg_scream`, `metal_gear_alert`, `explosion`, `bruh`, `shocked`, `faaah`, `death`, `gunshot`, `sad_violin`, `duck_toy`, `aayein`, `awkward`. Trim long/looping samples to ~1–2 s so they don't overstay.
- Mix: decode SFX to float mono @48k, place at exact timestamps at reduced gain, write one SFX WAV, then `amix` voice + SFX with `normalize=0`, trim to exact output duration.
- Example SFX assets and timeline: `projects\stream_02-18-49\sfx\meme\`, `projects\stream_02-18-49\render.py` (`EVENTS` list).

### Workflow rule (unchanged, reaffirmed)
- **Always show a storyboard preview for approval before rendering.** No exceptions.

Machine-readable copy: `D:\AI Video Editor\presets\stream_reel_preset.json`.

