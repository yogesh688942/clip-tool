"""Karaoke highlight renderer.

The complete caption is visible from cue start in a dimmed state; each item
eases smoothly to full brightness at its word timestamp. Text never vanishes
mid-sentence, so it cannot go missing while the speaker is still talking.
"""
import numpy as np
from PIL import Image
from word_caption import build_word_layers

DIM_FACTOR = 0.50
DIM_FLOOR = 25


def _dim(arr):
    out = arr.copy()
    out[:, :, :3] = np.clip(
        arr[:, :, :3].astype(np.float32) * DIM_FACTOR + DIM_FLOOR, 0, 255
    ).astype(np.uint8)
    return out


def build_karaoke(cue, scale=4 / 3, split=820, W=1440, H=2560):
    """Return a dim base overlay plus per-item bright tiles with highlight times."""
    layers = build_word_layers(cue, scale=scale, split=split, W=W, H=H)

    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for el in layers:
        base.alpha_composite(Image.fromarray(_dim(el["arr"]), "RGBA"),
                             (el["x0"], el["y0"]))

    arr = np.array(base)
    ys, xs = np.where(arr[:, :, 3] > 0)
    if not len(ys):
        return None
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1

    highlights = [
        {"t": float(el["t"]), "y": int(el["y0"] - y0), "x": int(el["x0"] - x0),
         "arr": el["arr"]}
        for el in layers
    ]
    return {"y0": y0, "x0": x0, "base": arr[y0:y1, x0:x1], "highlights": highlights}
