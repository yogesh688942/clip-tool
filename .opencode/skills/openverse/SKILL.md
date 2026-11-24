---
name: openverse
description: Search and download free Creative-Commons recorded sound effects, foley and ambiences from the public Openverse audio library, with licence filtering and automatic attribution. Use whenever the user asks for a free sound effect, CC sound, Creative Commons audio, "openverse sound", a whoosh/click/pop/impact/ambience to add to a reel, or wants more meme SFX options than the local library. Never use it to add a beat song to a stream reel - that is forbidden by the saved clip recipe.
---

# Openverse — free recorded sounds

Public API, no key, no extra Python packages. The helper script lives next to
this file at `scripts/openverse.py`. Paths below are relative to this skill's
directory.

## Rules for this project

- **No beat song.** Use it only for sparse SFX at crazy moments, as the saved
  clip recipe requires. Voice stays primary.
- Prefer `cc0` results. They need no attribution, but write credits anyway.
- For `cc-by` / `cc-by-sa`, always keep the generated `CREDITS.md` next to the
  sound files and respect any share-alike condition.
- Never cut, re-time or shorten a supplied clip when adding these sounds.

## Search

```bash
python scripts/openverse.py search "cartoon boing" --license cc0 --limit 8
python scripts/openverse.py search "whoosh" --license any --limit 5 --json
```

Each result prints its **id**, licence, duration, title, creator and source page.

## Download one sound

```bash
python scripts/openverse.py download <id> --out "D:\AI Video Editor\assets\sfx\boing.mp3" --credits "D:\AI Video Editor\assets\sfx\CREDITS.md"
```

## Search + download the top N

```bash
python scripts/openverse.py fetch "metal gear alert" --dir "D:\AI Video Editor\assets\sfx" --limit 3
```

This writes numbered files plus `CREDITS.md` in the target folder.

## Print credits for an id

```bash
python scripts/openverse.py credits <id>
```

## Notes

- Openverse previews are often short MP3 previews hosted by Freesound; that is
  fine for one-shot SFX. Check the printed duration before placing a cue.
- If a search returns nothing useful, try a plainer word (`alert`, `scream`,
  `impact`, `boing`) or `--license any`.
- The API can be slow or rate-limited; retry once before giving up.
