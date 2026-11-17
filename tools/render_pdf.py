"""Render a Markdown document from this repository to HTML, PDF and Word (.docx).

The Markdown stays the only source. Relative links to other repository files are
rewritten to their GitHub URLs, so they still work when the PDF or .docx is sent
on its own.

Needs: pandoc (https://pandoc.org), Google Chrome (for the PDF) and rsvg-convert
from librsvg (SVG to PNG for Word). On macOS: brew install pandoc librsvg.
Usage (from the repository root):
    python tools/render_pdf.py proposal/pitch.md     # writes build/pitch.html, build/pitch.pdf, build/pitch.docx
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GITHUB = "https://github.com/gsantopaolo/spacefom2-protobuf/blob/main/"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = Path(__file__).with_name("print.css")

LINK = re.compile(r"\]\((?!https?:|mailto:|#|/)([^)#\s]+)(#[^)\s]*)?\)")
HTML_IMG = re.compile(r'<p align="center"><img src="([^"]+)" alt="([^"]*)"[^>]*></p>')


def prepare(source: Path, raster_dir: Path | None = None) -> str:
    """Rewrite relative links to GitHub URLs and centred HTML images to Markdown images.

    With raster_dir, SVG images are converted to PNG there (for Word, which
    shows SVG only in recent versions).
    """
    text = source.read_text(encoding="utf-8")

    def link(m):
        target = (source.parent / m.group(1)).resolve().relative_to(REPO).as_posix()
        return f"]({GITHUB}{target}{m.group(2) or ''})"

    def image(m):
        path = (source.parent / m.group(1)).resolve()
        if raster_dir and path.suffix == ".svg":
            png = raster_dir / f"{path.stem}.png"
            subprocess.run(["rsvg-convert", "--zoom=2", "--output", str(png), str(path)], check=True)
            path = png
        return f"![{m.group(2)}]({path}){{width=66%}}"

    text = HTML_IMG.sub(image, text)
    # Images first become absolute paths, so the link rule leaves them alone.
    return LINK.sub(link, text)


def pandoc(markdown_text: str, out: Path, *extra: str) -> None:
    subprocess.run(
        ["pandoc", "--from=gfm+attributes", "--output", str(out), *extra],
        input=markdown_text, text=True, check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="Markdown file inside the repository")
    parser.add_argument("--out", type=Path, default=REPO / "build", help="output folder (default: build/)")
    args = parser.parse_args()

    source = args.source.resolve()
    text = prepare(source)
    title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), source.stem)
    args.out.mkdir(parents=True, exist_ok=True)
    stem = args.out / source.stem

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as css_header:
        css_header.write(f"<style>{CSS.read_text(encoding='utf-8')}</style>")
    html = stem.with_suffix(".html")
    pandoc(text, html, "--standalone", "--embed-resources", f"--metadata=pagetitle:{title}",
           f"--include-in-header={css_header.name}", "--template", str(Path(__file__).with_name("page.html")))
    Path(css_header.name).unlink()

    pdf = stem.with_suffix(".pdf")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html.resolve().as_uri()], check=True, capture_output=True)

    docx = stem.with_suffix(".docx")
    with tempfile.TemporaryDirectory() as raster_dir:
        pandoc(prepare(source, Path(raster_dir)), docx)

    for path in (html, pdf, docx):
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
