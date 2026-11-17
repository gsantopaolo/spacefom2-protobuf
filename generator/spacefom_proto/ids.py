"""Stable field numbers, kept in generator/field-ids.lock.json (plan §4).

A field keeps its number for as long as it exists. A new field gets
max(used and retired) + 1, skipping 19000-19999. A removed field is retired
and emitted as `reserved`. A reviewer can map a renamed field to its old
name in "renames" so it keeps the old number.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path

from .model import GeneratorError

LOCK_FORMAT = 1
FIRST_RESERVED_RANGE = range(19000, 20000)  # reserved for the protobuf implementation
MAX_FIELD_NUMBER = 536_870_911


@dataclass
class Changes:
    added: list[tuple[str, str, int]] = field(default_factory=list)
    retired: list[tuple[str, str, int]] = field(default_factory=list)
    renamed: list[tuple[str, str, str, int]] = field(default_factory=list)
    new_messages: list[str] = field(default_factory=list)
    removed_messages: list[str] = field(default_factory=list)

    def needs_review(self) -> list[str]:
        """Messages that gained and lost fields in one run: possible renames."""
        added = {m for m, _, _ in self.added if m not in self.new_messages}
        return sorted(added & {m for m, _, _ in self.retired})

    def empty(self) -> bool:
        return not (self.added or self.retired or self.renamed or self.removed_messages)


def empty_lock() -> dict:
    return {"format": LOCK_FORMAT, "messages": {}, "renames": {}}


def load_lock(path: Path) -> dict:
    if not path.exists():
        return empty_lock()
    lock = json.loads(path.read_text(encoding="utf-8"))
    if lock.get("format") != LOCK_FORMAT:
        raise GeneratorError(f"{path}: unsupported lock format {lock.get('format')!r}")
    lock.setdefault("messages", {})
    lock.setdefault("renames", {})
    return lock


def dump_lock(lock: dict) -> str:
    out = {"format": lock["format"], "messages": {}, "renames": {}}
    for name in sorted(lock["messages"]):
        entry = lock["messages"][name]
        out["messages"][name] = {
            "fields": dict(sorted(entry.get("fields", {}).items(), key=lambda kv: kv[1])),
            "retired": sorted(entry.get("retired", []), key=lambda r: (r["number"] is None, r["number"] or 0, r["name"])),
        }
    for name in sorted(lock["renames"]):
        out["renames"][name] = dict(sorted(lock["renames"][name].items()))
    return json.dumps(out, indent=2, ensure_ascii=False) + "\n"


def _next_number(used: set[int]) -> int:
    n = max(used, default=0) + 1
    if n in FIRST_RESERVED_RANGE:
        n = FIRST_RESERVED_RANGE.stop
    if n > MAX_FIELD_NUMBER:
        raise GeneratorError("field numbers exhausted")
    return n


def assign(lock: dict, messages: dict[str, list[str]]) -> tuple[dict, Changes]:
    """Return the updated lock and what changed.

    `messages` maps each message name to its field names in FOM order.
    """
    lock = copy.deepcopy(lock)
    changes = Changes()
    for msg in messages:
        if msg not in lock["messages"]:
            changes.new_messages.append(msg)
        entry = lock["messages"].setdefault(msg, {"fields": {}, "retired": []})
        entry.setdefault("fields", {})
        entry.setdefault("retired", [])
        fields, retired = entry["fields"], entry["retired"]
        wanted = messages[msg]
        if len(set(wanted)) != len(wanted):
            raise GeneratorError(f"{msg}: duplicate field names {wanted}")

        # Reviewer-curated renames: new name takes over the old name's number.
        for new, old in lock["renames"].get(msg, {}).items():
            if new in fields or new not in wanted:
                continue
            if old in fields and old not in wanted:
                number = fields.pop(old)
            else:
                match = [r for r in retired if r["name"] == old and r["number"] is not None]
                if not match:
                    continue
                number = match[-1]["number"]
                retired.remove(match[-1])
                # The old name stays reserved; only the number moves.
                retired.append({"name": old, "number": None})
            fields[new] = number
            changes.renamed.append((msg, old, new, number))

        for name in [n for n in fields if n not in wanted]:
            number = fields.pop(name)
            retired.append({"name": name, "number": number})
            changes.retired.append((msg, name, number))

        used = set(fields.values()) | {r["number"] for r in retired if r["number"] is not None}
        for name in wanted:
            if name not in fields:
                fields[name] = _next_number(used)
                used.add(fields[name])
                changes.added.append((msg, name, fields[name]))

    for msg in sorted(set(lock["messages"]) - set(messages)):
        entry = lock["messages"][msg]
        if entry["fields"]:
            changes.removed_messages.append(msg)
        for name, number in list(entry["fields"].items()):
            entry["retired"].append({"name": name, "number": number})
            changes.retired.append((msg, name, number))
        entry["fields"] = {}
    return lock, changes


def reserved(entry: dict) -> tuple[list[int], list[str]]:
    """Numbers and names to emit as `reserved` for a message's lock entry."""
    numbers = sorted({r["number"] for r in entry["retired"] if r["number"] is not None})
    live = set(entry["fields"])
    names = sorted({r["name"] for r in entry["retired"]} - live)
    return numbers, names
