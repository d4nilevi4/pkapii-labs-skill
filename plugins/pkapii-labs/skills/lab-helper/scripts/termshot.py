"""Render a terminal-window PNG from a real transcript (commands and their output).
  python3 termshot.py transcript.txt out.png ["window title"]
Lines are drawn as they are; lines that look like a shell prompt are colored. macOS only (uses Menlo)."""
import re, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 15)
BOLD = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 15, index=1)
COLS, PAD, TOP = 112, 14, 34
CW = int(FONT.getlength("M"))
LH = 20
PROMPT_RE = re.compile(r"^(\S+@\S+:\S*[$#]) (.*)$")
EMOJI = re.compile("[\U0001F000-\U0001FFFF\uFE0F]")  # Menlo has no emoji: dropped in the image only, the log keeps them
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07")

def lines_of(text):
    out = []
    for raw in EMOJI.sub("", ANSI.sub("", text)).replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        raw = raw.expandtabs(8)
        out += textwrap.wrap(raw, COLS, drop_whitespace=False, replace_whitespace=False) or [""]
    while out and not out[-1].strip():
        out.pop()
    return out

def render(text, path, title="user@vm: ~"):
    ls = lines_of(text)
    w, h = COLS * CW + 2 * PAD, TOP + len(ls) * LH + PAD
    im = Image.new("RGB", (w, h), (30, 30, 30))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, 28], fill=(58, 58, 60))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([12 + 20 * i, 8, 24 + 20 * i, 20], fill=c)
    d.text((w // 2 - len(title) * CW // 2, 6), title, font=FONT, fill=(200, 200, 200))
    y = TOP
    for l in ls:
        m = PROMPT_RE.match(l)
        if m:
            d.text((PAD, y), m.group(1), font=BOLD, fill=(120, 220, 120))
            d.text((PAD + (len(m.group(1)) + 1) * CW, y), m.group(2), font=FONT, fill=(255, 255, 255))
        else:
            d.text((PAD, y), l, font=FONT, fill=(215, 215, 215))
        y += LH
    im.save(path)

if __name__ == "__main__":
    render(open(sys.argv[1]).read(), sys.argv[2], *(sys.argv[3:4]))
