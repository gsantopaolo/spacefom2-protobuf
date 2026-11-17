"""Check every relative link and #anchor in the repository's Markdown (issue #29, m9).

For each tracked *.md file it checks:
  - that a relative link target (file or folder) exists, and
  - that a #fragment pointing into a Markdown file names a heading or an
    explicit HTML id/name in that file.

Heading anchors follow GitHub's rules, as implemented by github-slugger
(https://github.com/Flet/github-slugger, index.js and script/generate-regex.js):
lowercase the rendered heading text, drop punctuation other than "-" and "_",
symbols, separators other than " ", control characters and "other" numbers
such as superscripts, turn each space into a hyphen, and number repeats -1, -2,
... in document order. Symbols that Unicode also calls alphabetic (circled
letters, for example) are dropped here but kept by GitHub.

External links (anything with a URL scheme, such as https: or mailto:) are out
of scope. Fragments into files that are not Markdown (for example #L10 on
source code) are not checked. Code blocks, code spans and HTML comments are
ignored.

Usage:
  python tools/check_links.py [--root DIR] [FILE.md ...]

With no files it checks every *.md file tracked by git under --root (default:
the repository that contains the current directory). Prints one line per broken
link and exits 1 if there are any.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote

# Unicode general categories github-slugger removes (besides " " and "-").
SLUG_DROPPED = {
    "No",
    *("Pd", "Pe", "Pf", "Pi", "Po", "Ps"),
    *("Sc", "Sk", "Sm", "So"),
    *("Cc", "Co", "Cf", "Cn"),
    *("Zl", "Zp", "Zs"),
}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
CODE_SPAN = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
# [text](target) and ![alt](target); the target may be <...> and may have a title.
INLINE_LINK = re.compile(
    r"!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]"  # [text], one level of nested brackets
    r"\(\s*(<[^>]*>|[^\s()]*(?:\([^\s()]*\)[^\s()]*)*)"  # (target, balanced parentheses
)
# [label]: target, but not a footnote ([^1]: text).
REFERENCE_DEF = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(<[^>]*>|\S+)", re.MULTILINE)
HTML_LINK = re.compile(r"""<(?:a|img)\b[^>]*?\b(?:href|src)\s*=\s*["']([^"']*)["']""", re.IGNORECASE)
HTML_ID = re.compile(r"""<[a-zA-Z][^>]*?\b(?:id|name)\s*=\s*["']([^"']+)["']""")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
INLINE_MARKUP = re.compile(r"!?\[([^\]]*)\]\([^)]*\)|<[^>]+>|[*~]+|(?<![\w])_+|_+(?![\w])")


@dataclass(frozen=True)
class Broken:
    file: Path
    line: int
    target: str
    reason: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.target}: {self.reason}"


def slugify(text: str) -> str:
    """GitHub's heading id for already rendered heading text (github-slugger)."""
    kept = (c for c in text.lower() if c in " -" or unicodedata.category(c) not in SLUG_DROPPED)
    return "".join(kept).replace(" ", "-")


def _unique(slug: str, occurrences: dict[str, int]) -> str:
    """github-slugger's de-duplication: the first repeat of "a" is "a-1"."""
    result = slug
    while result in occurrences:
        occurrences[slug] += 1
        result = f"{slug}-{occurrences[slug]}"
    occurrences[result] = 0
    return result


def heading_text(markdown: str) -> str:
    """The plain text GitHub renders for a heading's inline Markdown."""
    text = CODE_SPAN.sub(lambda m: m.group(2).strip(), markdown)
    text = INLINE_MARKUP.sub(lambda m: m.group(1) or "", text)
    return text.strip()


def _blank_code(lines: list[str]) -> list[str]:
    """Replace fenced code block lines with empty strings, keeping line numbers."""
    out, fence = [], None
    for line in lines:
        match = FENCE.match(line)
        if fence is None and match:
            fence = match.group(1)
            out.append("")
        elif fence is not None:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            out.append("")
        else:
            out.append(line)
    return out


def _prose(text: str) -> str:
    """The Markdown with comments, fenced code and code spans blanked out.

    Blanking keeps every character's line number, so matches can be reported
    by line.
    """
    text = HTML_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    text = "\n".join(_blank_code(text.split("\n")))
    return CODE_SPAN.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def anchors(text: str) -> set[str]:
    """Every fragment a link may use for a Markdown document."""
    found: set[str] = set()
    occurrences: dict[str, int] = {}
    lines = _blank_code(HTML_COMMENT.sub("", text).split("\n"))
    for i, line in enumerate(lines):
        atx = ATX_HEADING.match(line)
        if atx:
            title = atx.group(2) or ""
        elif (
            i > 0
            and SETEXT_UNDERLINE.match(line)
            and lines[i - 1].strip()
            and not ATX_HEADING.match(lines[i - 1])
            and not (line.strip().startswith("-") and lines[i - 1].lstrip().startswith(("-", "*", "+")))
        ):
            title = lines[i - 1]
        else:
            continue
        found.add(_unique(slugify(heading_text(title)), occurrences))
    found.update(HTML_ID.findall(_prose(text)))
    return found


def link_targets(text: str) -> list[tuple[int, str]]:
    """(line, target) for every link in the Markdown outside code and comments."""
    prose = _prose(text)
    targets = []
    for pattern in (INLINE_LINK, REFERENCE_DEF, HTML_LINK):
        for match in pattern.finditer(prose):
            target = match.group(1)
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            targets.append((prose.count("\n", 0, match.start(1)) + 1, target))
    return sorted(targets)


@lru_cache(maxsize=None)
def _anchors_of(path: Path) -> frozenset[str]:
    return frozenset(anchors(path.read_text(encoding="utf-8")))


def check_file(md: Path, root: Path) -> list[Broken]:
    """Broken relative links and anchors in one Markdown file."""
    root = root.resolve()
    rel = md.resolve().relative_to(root)
    broken = []
    for line, target in link_targets(md.read_text(encoding="utf-8")):
        if not target or SCHEME.match(target) or target.startswith("//"):
            continue
        path_part, _, fragment = target.partition("#")
        path_part = unquote(path_part.split("?", 1)[0])
        if path_part.startswith("/"):
            dest = root / path_part.lstrip("/")
        elif path_part:
            dest = md.resolve().parent / path_part
        else:
            dest = md.resolve()
        dest = dest.resolve()
        if not dest.is_relative_to(root):
            broken.append(Broken(rel, line, target, "points outside the repository"))
        elif not dest.exists():
            broken.append(Broken(rel, line, target, "no such file or folder"))
        elif fragment and dest.is_file() and dest.suffix.lower() == ".md":
            if unquote(fragment) not in _anchors_of(dest):
                broken.append(Broken(rel, line, target, f"no heading or id #{fragment} in {dest.relative_to(root)}"))
    return broken


def tracked_markdown(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", "*.md"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [root / name for name in result.stdout.split("\0") if name]


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True, text=True
    )
    return Path(result.stdout.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, help="repository root (default: from git)")
    parser.add_argument("files", nargs="*", type=Path, help="Markdown files (default: all tracked *.md)")
    args = parser.parse_args(argv)

    root = (args.root or repo_root()).resolve()
    files = args.files or tracked_markdown(root)
    broken = [b for md in files for b in check_file(md, root)]
    for b in broken:
        print(b)
    print(f"Checked {len(files)} Markdown files: {len(broken)} broken links.", file=sys.stderr)
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
