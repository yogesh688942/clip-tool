# Third-party skills bundled here

These skill folders are copied unmodified from their upstream projects, apart
from being placed in OpenCode's `skills/` layout.

| Skill | Upstream | Licence |
| --- | --- | --- |
| `real-sfx/` | <https://github.com/Clipwing/skills> (`skills/real-sfx`) | Scripts MIT; bundled UI sounds CC0 1.0 (`LICENSE-uisfx-audio.txt`) |
| `earshot/` | <https://github.com/Leonxlnx/earshot> (`skills/earshot`) | MIT — see `LICENSE-earshot.txt` |
| `real-sound/` | <https://github.com/Leonxlnx/earshot> (`skills/real-sound`) | MIT — see `LICENSE-earshot.txt` |
| `openverse/` | Written for this project | Uses the public Openverse API <https://api.openverse.org/>; downloaded audio keeps its own CC licence and is credited in `CREDITS.md` |

The `earshot` Python package itself is installed from GitHub into the virtualenv
by `install.py`, not vendored in this repository.
