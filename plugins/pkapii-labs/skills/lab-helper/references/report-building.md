# Building Word and PDF documents: tools and pitfalls

Tool-level hints from the original run. They say nothing about how a report should look: fonts, margins, spacing, title page and numbering come from the student's department. In the original run the result did not follow GOST. Values written as `<...>` are the student's.

## Tools used (macOS, Homebrew)

| Tool | Role |
|---|---|
| `pandoc` | Markdown to LaTeX and to docx; also LaTeX to docx |
| `xelatex` (MacTeX) | PDF with system fonts and Cyrillic |
| `python-docx` (`pip install python-docx`) | Post-processing a docx that pandoc produced |
| LibreOffice (`soffice`) | Convert docx to PDF to see how it renders, without opening Word |
| poppler (`pdftoppm`, `pdftotext`, `pdfinfo`) | Page images, text and page counts for checks |
| Pillow | Used by `scripts/check_pdf_overflow.py` and the screenshot scripts |

Word itself was not used; docx files were checked only through LibreOffice. Rendering in real Word can differ slightly.

## Route that was used

One markdown source per document, two outputs:

```bash
# PDF: pandoc makes the body, your own preamble wraps it, xelatex builds it
pandoc report.md -f markdown+smart -t latex -o body.tex
xelatex -interaction=nonstopmode -halt-on-error report.tex

# docx: pandoc with a reference document, then python-docx for what pandoc cannot do
pandoc -o ref.docx --print-default-data-file reference.docx      # edit styles in it, or by python-docx
pandoc report.md -f markdown+smart -o report.docx --reference-doc ref.docx
```

A one-liner without a custom preamble also works for a quick PDF:
`pandoc report.md --pdf-engine=xelatex -V lang=ru -V mainfont="<font>" -V monofont="<mono font>" -o report.pdf`.

Pandoc's default figure caption in the PDF reads "Рис. 1: ..."; a different caption format needs `caption`/`\captionsetup` in the preamble.

**LaTeX to Word.** `pandoc report.tex -o report.docx` converts plain LaTeX, but custom packages and the preamble are lost. That is why the docx was built from the markdown source and not from the `.tex`. Converting in the other direction (docx to PDF) was done with LibreOffice:

```bash
soffice --headless --convert-to pdf --outdir /tmp/docx_pdf report.docx
```

What `python-docx` was used for after pandoc: inserting a title page copied from the student's own sample docx (opening the sample, changing the text of its fields, adding the XML to the document body), setting fonts and spacing on styles, a page-number field in the footer, "Figure N –" prefixes on captions, centering image paragraphs and removing their first-line indent, borders on tables, and capping the size of pictures.

## Checks after every build

```bash
pdfinfo report.pdf | grep Pages                  # compare PDF and docx-through-LibreOffice page counts
pdftoppm -r 60 -png report.pdf /tmp/pg           # look at pages as images
python3 scripts/check_pdf_overflow.py report.pdf --bottom <cm> --right <cm>
```

`check_pdf_overflow.py` counts dark pixels in the band between the text area and the page number, and past the right margin. It was added after a figure that overlapped the page number went unnoticed. Run it on the PDF and on the PDF that LibreOffice makes from the docx. In the LaTeX log, search for `Overfull \hbox`.

## Pitfalls and fixes

| Problem | Fix |
|---|---|
| `fvextra` is missing in the TeX installation, so long code lines do not wrap | Use `fancyvrb` and wrap long lines yourself before building |
| Cyrillic does not render in the monospace font (Menlo, Courier New with polyglossia) | Pick a mono font with Cyrillic, such as PT Mono, through `\setmonofont` |
| pandoc tables fail with an undefined `none` counter | `\newcounter{none}` in the preamble |
| Newer pandoc emits `\pandocbounded` | `\newcommand{\pandocbounded}[1]{#1}` |
| pandoc's default docx styles override the title page | Use your own reference docx, and set spacing on the title page explicitly |
| Heading fonts in Word come from the theme (Calibri/Cambria) | Set the font explicitly on heading styles (ascii, hAnsi, eastAsia) and drop the theme attributes |
| Tall terminal screenshots run into the page number | Split them into parts that each fit a page, or cap the height (`height=0.78\textheight,keepaspectratio`); in docx cap the picture size in python-docx |
| A figure without caption is shifted right | The first-line indent applies to it: `\setlength{\parindent}{0pt}` and `\centering` in the figure, and in docx no first-line indent plus centered alignment |
| Overfull lines | `\sloppy`, `\emergencystretch=4em`, `\allowbreak` after `, / = : .` inside `\texttt`; turn very wide tables into lists |
| Figure references in the text drift after inserting a figure | Reference numbers are typed by hand, so re-check all of them after any insertion |
| LibreOffice writes the PDF next to the docx | `--outdir` into a temporary folder |

## Habits

- Rebuild after every edit to the source and rerun the checks.
- Keep a copy of every deliverable in a separate folder after each rebuild, so an old version is never sent by mistake.
- Keep personal data (name, group) in one place of the build script or in the sample, so it can be replaced in one step.
- Report prose reads better after a pass with the separate `/humanizer` skill, which removes typical signs of machine-written text. It is not part of this repository and is installed on its own.
