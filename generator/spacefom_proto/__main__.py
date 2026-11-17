"""Command line: python -m spacefom_proto {generate,fetch,archive} (run with PYTHONPATH=generator)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .archive import archive
from .emit import PACKAGE_DIR
from .fetch import fetch
from .generate import generate, load_source, report, verify_inputs
from .ids import load_lock
from .model import GeneratorError


def _generate(args) -> int:
    source = load_source(args.source)
    paths = verify_inputs(args.fom_dir, source)
    result = generate(paths, load_lock(args.lock), not args.no_semantics, not args.no_interactions)
    if args.report:
        args.report.write_text(report(result.changes), encoding="utf-8")

    package_dir = args.out / PACKAGE_DIR
    existing = {p.relative_to(args.out).as_posix() for p in package_dir.glob("*.proto")}
    stale = sorted(existing - set(result.files))
    changed = sorted(
        rel for rel, text in result.files.items()
        if not (args.out / rel).is_file() or (args.out / rel).read_text(encoding="utf-8") != text
    )
    lock_changed = not args.lock.is_file() or args.lock.read_text(encoding="utf-8") != result.lock_text

    if args.check:
        problems = [f"{args.out / r} is out of date" for r in changed]
        problems += [f"{args.out / r} is not generated" for r in stale]
        if lock_changed:
            problems.append(f"{args.lock} is out of date")
        for p in problems:
            print(p, file=sys.stderr)
        if problems:
            print("Run the generator and commit the result.", file=sys.stderr)
            return 1
        print("Generated files are up to date.")
        return 0

    for rel in stale:
        (args.out / rel).unlink()
    for rel in changed:
        path = args.out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(result.files[rel], encoding="utf-8", newline="\n")
    if lock_changed:
        args.lock.write_text(result.lock_text, encoding="utf-8", newline="\n")
    print(f"{len(changed)} file(s) written, {len(stale)} removed, lock {'updated' if lock_changed else 'unchanged'}.")
    return 0


def _fetch(args) -> int:
    for path in fetch(load_source(args.source), args.dest):
        print(path)
    return 0


def _archive(args) -> int:
    target = archive(args.proto, args.history, args.main_commit)
    print(target if target else "nothing to archive")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spacefom_proto")
    sub = parser.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="generate .proto files from the FOM modules")
    g.add_argument("--fom-dir", type=Path, required=True)
    g.add_argument("--source", type=Path, default=Path("fom/SOURCE.json"))
    g.add_argument("--out", type=Path, default=Path("proto"))
    g.add_argument("--lock", type=Path, default=Path("generator/field-ids.lock.json"))
    g.add_argument("--no-semantics", action="store_true", help="leave FOM <semantics> text out of comments")
    g.add_argument("--no-interactions", action="store_true", help="do not emit interaction classes")
    g.add_argument("--check", action="store_true", help="write nothing; fail if committed output is stale")
    g.add_argument("--report", type=Path, help="write a Markdown summary of field-number changes")
    g.set_defaults(func=_generate)

    f = sub.add_parser("fetch", help="download the pinned FOM modules and check sha256")
    f.add_argument("--source", type=Path, default=Path("fom/SOURCE.json"))
    f.add_argument("--dest", type=Path, required=True)
    f.set_defaults(func=_fetch)

    a = sub.add_parser("archive", help="copy the current proto tree into history/")
    a.add_argument("--proto", type=Path, required=True)
    a.add_argument("--history", type=Path, default=Path("history"))
    a.add_argument("--main-commit", required=True)
    a.set_defaults(func=_archive)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except GeneratorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
