"""Add the SISO attribution to every generated file under samples/generated/.

The FOM modules allow use of their schema "provided that any use of the
material contains the following attribution: 'Reprinted with permission from
SISO Inc.'". protoc keeps the .proto header comment for Go and TypeScript but
drops it for C++, Java, C# and Python, so this script adds it after
`buf generate`. Running it again changes nothing.

Usage (from the repository root):
    python samples/attribution.py           # add where missing
    python samples/attribution.py --check   # fail if any file lacks it
"""

import sys
from pathlib import Path

GENERATED = Path(__file__).resolve().parent / "generated"
ATTRIBUTION = "Reprinted with permission from SISO Inc."
HEADER = ["Derived from the SISO-STD-018-2020 (SpaceFOM) FOM modules.", ATTRIBUTION]
COMMENT = {
    ".h": "//", ".cc": "//", ".java": "//", ".cs": "//", ".go": "//",
    ".js": "//", ".ts": "//", ".py": "#", ".pyi": "#",
}


def files():
    """Generated source files (skips caches such as __pycache__/*.pyc)."""
    return sorted(
        p for p in GENERATED.rglob("*")
        if p.is_file() and p.suffix in COMMENT and "__pycache__" not in p.parts
    )


def add(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if ATTRIBUTION in text:
        return False
    prefix = COMMENT[path.suffix]
    header = "".join(f"{prefix} {line}\n" for line in HEADER)
    lines = text.splitlines(keepends=True)
    # Keep a Python coding declaration on the first line.
    keep = 1 if lines and lines[0].startswith("#") and "coding" in lines[0] else 0
    path.write_text("".join(lines[:keep]) + header + "".join(lines[keep:]), encoding="utf-8")
    return True


def main() -> int:
    if "--check" in sys.argv[1:]:
        missing = [p for p in files() if ATTRIBUTION not in p.read_text(encoding="utf-8")]
        for p in missing:
            print(f"missing SISO attribution: {p.relative_to(GENERATED.parent)}", file=sys.stderr)
        return 1 if missing else 0
    changed = sum(add(p) for p in files())
    print(f"attribution added to {changed} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
