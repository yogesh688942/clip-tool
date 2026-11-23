"""Draw a caption cue (pop word + dense line) with Twemoji inline, at any scale.

Portable version: fonts and emoji are resolved relative to this repo.
"""
import os
from PIL import Image, ImageDraw, ImageFont
from paths import FONT_DIR, EMOJI_DIR

FONT_CANDIDATES = [
    FONT_DIR / "Montserrat-Variable.ttf",
]

# Platform fallbacks, used only if the bundled font cannot be loaded.
FALLBACKS = [
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

MINT, RED, YELLOW, BLACK = "#1EE3B2", "#FF3B30", "#FFD400", "#000000"


def font(size):
    size = max(1, int(size))
    for path in FONT_CANDIDATES:
        try:
            f = ImageFont.truetype(str(path), size)
            try:
                f.set_variation_by_axes([800])
            except Exception:
                pass
            return f
        except Exception:
            pass
    for path in FALLBACKS:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def emoji_img(code, size):
    path = os.path.join(str(EMOJI_DIR), code + ".png")
    im = Image.open(path).convert("RGBA")
    return im.resize((max(1, int(size)), max(1, int(size))), Image.Resampling.LANCZOS)


def render_cue(im, cue, scale=1.0, split=820):
    """Draw the cue onto transparent RGBA image `im` using base coords * scale.

    `split` is the y coordinate of the panel split in the 1080x1920 base space.
    """
    d = ImageDraw.Draw(im)
    cx = im.width / 2
    y_split = split * scale
    pop_f, dense_f = font(80 * scale), font(48 * scale)
    pop_stroke, dense_stroke = max(1, round(12 * scale)), max(1, round(9 * scale))

    first = cue["text"].split(" ")[0]
    pw = d.textlength(first, font=pop_f)
    pop_y = y_split - 45 * scale
    d.text((cx - pw / 2, pop_y), first, font=pop_f, fill=YELLOW,
           anchor="lm", stroke_width=pop_stroke, stroke_fill=BLACK)

    pe = emoji_img(cue["pop_emoji"], 88 * scale)
    px = cx + pw / 2 + 14 * scale
    im.paste(pe, (int(px), int(pop_y - pe.height / 2)), pe)

    words = cue["text"].split(" ")
    if len(words) <= 6:
        lines = [words]
    else:
        half = len(words) // 2
        lines = [words[:half], words[half:]]
    y = y_split + 45 * scale
    for li, line in enumerate(lines):
        widths = [d.textlength(w, font=dense_f) for w in line]
        space = d.textlength(" ", font=dense_f)
        inline = cue.get("inline_emoji") if li == 0 else None
        ie = emoji_img(inline["code"], 44 * scale) if inline else None
        gap = (ie.width + space) if ie else 0
        total = sum(widths) + space * (len(line) - 1) + gap
        x = cx - total / 2
        for wi, (w, ww) in enumerate(zip(line, widths)):
            col = RED if w.upper() in cue["hl"] else MINT
            d.text((x, y), w, font=dense_f, fill=col, anchor="lm",
                   stroke_width=dense_stroke, stroke_fill=BLACK)
            x += ww + space
            if ie and wi == inline["after"]:
                im.paste(ie, (int(x - space), int(y - ie.height / 2)), ie)
                x += ie.width + space
        y += 54 * scale
    return im
