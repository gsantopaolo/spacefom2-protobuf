"""Tie parsing, mapping, numbering and emitting together."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .emit import PACKAGE_DIR, render
from .ids import Changes, assign, dump_lock
from .mapping import Mapper, ProtoMessage
from .model import GeneratorError
from .parse import module_key, parse_module


@dataclass
class Result:
    files: dict[str, str]  # path relative to the proto root -> content
    lock: dict
    lock_text: str
    changes: Changes


def load_source(path: Path) -> dict:
    source = json.loads(path.read_text(encoding="utf-8"))
    if not source.get("files"):
        raise GeneratorError(f"{path}: no files listed")
    return source


def verify_inputs(fom_dir: Path, source: dict) -> list[Path]:
    """Check every pinned file exists in fom_dir with the pinned sha256."""
    paths = []
    for entry in source["files"]:
        path = fom_dir / entry["name"]
        if not path.is_file():
            raise GeneratorError(f"missing FOM module {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise GeneratorError(
                f"{path}: sha256 {digest} does not match {entry['sha256']} in SOURCE.json"
            )
        paths.append(path)
    return paths


def generate(
    paths: list[Path],
    lock: dict,
    semantics: bool = True,
    interactions: bool = True,
) -> Result:
    modules = [parse_module(p) for p in paths]
    keys = [module_key(p.name) for p in paths]
    if len(set(keys)) != len(keys):
        raise GeneratorError(f"duplicate module names: {keys}")

    # Number every message, emitted or not, so --no-interactions never
    # retires the fields of a message that still exists in the FOM.
    all_files = Mapper(modules, interactions=True).map()
    messages = {
        item.name: [f.name for f in item.fields]
        for f in all_files
        for item in f.items
        if isinstance(item, ProtoMessage)
    }
    lock, changes = assign(lock, messages)

    files = {}
    for f in Mapper(modules, interactions=interactions).map():
        files[f"{PACKAGE_DIR}/{f.module.key}.proto"] = render(f, lock, semantics, interactions)
    return Result(files, lock, dump_lock(lock), changes)


def report(changes: Changes) -> str:
    """Markdown summary for the pull request body."""
    lines = ["## Field number changes", ""]
    if changes.empty() and not changes.new_messages:
        lines.append("No field numbers changed.")
        return "\n".join(lines) + "\n"
    if changes.new_messages:
        lines.append("New messages: " + ", ".join(f"`{m}`" for m in changes.new_messages))
        lines.append("")
    for title, rows in (
        ("Added fields", [f"`{m}.{f}` = {n}" for m, f, n in changes.added
                          if m not in changes.new_messages]),
        ("Retired fields (now `reserved`)", [f"`{m}.{f}` was {n}" for m, f, n in changes.retired]),
        ("Renamed fields (from the lock file `renames` map)",
         [f"`{m}.{old}` -> `{m}.{new}` keeps {n}" for m, old, new, n in changes.renamed]),
        ("Removed messages", [f"`{m}`" for m in changes.removed_messages]),
    ):
        if rows:
            lines.append(f"### {title}")
            lines.append("")
            lines.extend(f"- {r}" for r in rows)
            lines.append("")
    review = changes.needs_review()
    if review:
        lines.append("### Needs human review")
        lines.append("")
        lines.append(
            "These messages gained and lost fields in the same run. If a field was renamed, "
            "add it to `renames` in `generator/field-ids.lock.json` and rerun, so it keeps its number."
        )
        lines.append("")
        lines.extend(f"- `{m}`" for m in review)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
