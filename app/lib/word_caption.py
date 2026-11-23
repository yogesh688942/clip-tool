"""One RGBA tile per word at its final laid-out position, with a reveal time.

Used by the karaoke highlight profile. Emojis ride along with their word.
"""
import numpy as np
from PIL import Image, ImageDraw
from emoji_text import font, emoji_img, MINT, RED, YELLOW, BLACK


def _crop(draw_fn, W, H):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer), layer)
    arr = np.array(layer)
    ys, xs = np.where(arr[:, :, 3] > 0)
    if not len(ys):
        return None
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    return (y0, x0, arr[y0:y1, x0:x1])


def build_word_layers(cue, scale=1.0, split=820, W=1440, H=2560):
    """Return [{'t': reveal time, 'y0', 'x0', 'arr'}] word layers."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    cx = W / 2
    y_split = split * scale
    pop_f, dense_f = font(80 * scale), font(48 * scale)
    pop_stroke = max(1, round(12 * scale))
    dense_stroke = max(1, round(9 * scale))

    words = cue["text"].split(" ")
    reveal = [w["t"] for w in cue["words"]]
    assert len(words) == len(reveal), (cue["i"], len(words), len(reveal))
    layers = []

    def add(t, draw_fn):
        cropped = _crop(draw_fn, W, H)
        if cropped:
            y0, x0, arr = cropped
            layers.append({"t": float(t), "y0": y0, "x0": x0, "arr": arr})

    first = words[0]
    pw = dummy.textlength(first, font=pop_f)
    pop_y = y_split - 45 * scale
    pop_x = cx - pw / 2

    def draw_pop(d, _):
        d.text((pop_x, pop_y), first, font=pop_f, fill=YELLOW,
               anchor="lm", stroke_width=pop_stroke, stroke_fill=BLACK)
    add(reveal[0], draw_pop)

    pe = emoji_img(cue["pop_emoji"], 88 * scale)
    pex, pey = int(cx + pw / 2 + 14 * scale), int(pop_y - pe.height / 2)

    def draw_pop_emoji(_, im):
        im.paste(pe, (pex, pey), pe)
    add(reveal[0], draw_pop_emoji)

    if len(words) <= 6:
        lines = [words]
    else:
        half = len(words) // 2
        lines = [words[:half], words[half:]]
    inline = cue.get("inline_emoji")
    ie = emoji_img(inline["code"], 44 * scale) if inline else None
    after = inline["after"] if inline else -1

    y = y_split + 45 * scale
    gi = 0
    for line in lines:
        widths = [dummy.textlength(w, font=dense_f) for w in line]
        space = dummy.textlength(" ", font=dense_f)
        local_after = after - gi if (ie is not None and gi <= after < gi + len(line)) else None
        gap = (ie.width + space) if local_after is not None else 0
        total = sum(widths) + space * (len(line) - 1) + gap
        x = cx - total / 2
        for wi, (w, ww) in enumerate(zip(line, widths)):
            col = RED if w.upper() in cue["hl"] else MINT
            wx, wy = x, y

            def draw_word(d, _, _wx=wx, _wy=wy, _w=w, _col=col):
                d.text((_wx, _wy), _w, font=dense_f, fill=_col, anchor="lm",
                       stroke_width=dense_stroke, stroke_fill=BLACK)
            add(reveal[gi], draw_word)
            x += ww + space
            if local_after is not None and wi == local_after:
                ex, ey = int(x - space), int(y - ie.height / 2)

                def draw_inline(_, im, _ex=ex, _ey=ey):
                    im.paste(ie, (_ex, _ey), ie)
                add(reveal[gi], draw_inline)
                x += ie.width + space
            gi += 1
        y += 54 * scale

    return layers
