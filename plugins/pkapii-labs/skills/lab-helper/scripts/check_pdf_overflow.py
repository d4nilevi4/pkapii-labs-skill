"""Find pages where content (usually a tall figure) leaks into the bottom margin, onto the page number, or past the right margin.
  python3 check_pdf_overflow.py file.pdf [--bottom 2.5] [--right 1.0] [--number-gap 0.65] [--threshold 60]
--bottom / --right: the document's real bottom and right margins in cm (take them from your requirements).
--number-gap: how far below the text area (cm) the page number's top starts; the band between the text area and that point must stay empty.
Pages are rendered with pdftoppm (poppler) and dark pixels are counted. Works for a PDF made by LaTeX or by LibreOffice from a docx."""
import argparse, glob, os, subprocess, tempfile
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("pdf"); ap.add_argument("--bottom", type=float, default=2.5); ap.add_argument("--right", type=float, default=1.0)
ap.add_argument("--number-gap", type=float, default=0.65); ap.add_argument("--threshold", type=int, default=60)
ap.add_argument("--dpi", type=int, default=60)
a = ap.parse_args()
d = tempfile.mkdtemp()
subprocess.run(["pdftoppm", "-r", str(a.dpi), "-png", a.pdf, d + "/p"], check=True)
cm = a.dpi / 2.54
ink = lambda im: sum(1 for p in im.getdata() if p < 140)
bad = 0
for f in sorted(glob.glob(d + "/p-*.png")):
    im = Image.open(f).convert("L"); w, h = im.size
    text_bottom = h - a.bottom * cm
    band = im.crop((0, int(text_bottom + 0.1 * cm), w, int(text_bottom + a.number_gap * cm)))
    right = im.crop((int(w - (a.right - 0.2) * cm), 0, w, h))
    if ink(band) > a.threshold or ink(right) > a.threshold:
        bad += 1; print(os.path.basename(f), "bottom band:", ink(band), "right margin:", ink(right))
print(a.pdf, "pages with problems:", bad)
