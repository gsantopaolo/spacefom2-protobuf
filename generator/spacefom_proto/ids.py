"""Stable field numbers, kept in generator/field-ids.lock.json (plan §4).

A field keeps its number for as long as it exists. A new field gets
max(used and retired) + 1, skipping 19000-19999. A removed field is retired
and emitted as `reserved`.

The lock file is generator output. Renames are a reviewer-edited input in
generator/field-renames.json:

    {"Message": {"new_name": "old_name"}}

(an empty object when there are none). When the FOM renames a field, the
listed new name takes the old name's number and the old name stays reserved.
The rename must land before the new name gets a number of its own; if the
lock already numbers the new name differently, generation fails and says how
to fix it. An applied rename is recorded in the lock (`renamed_to` on the old
name's retired entry), so later runs skip it.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path

from .model import GeneratorError

# Format 2 moved `renames` out of the lock into field-renames.json and added
# `renamed_to` to retired entries. Format 1 locks are migrated on load.
LOCK_FORMAT = 2
RENAMES_FILE = "generator/field-renames.json"
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
    return {"format": LOCK_FORMAT, "messages": {}}


def load_lock(path: Path) -> dict:
    if not path.exists():
        return empty_lock()
    lock = json.loads(path.read_text(encoding="utf-8"))
    fmt = lock.get("format")
    if fmt == 1:
        if lock.pop("renames", {}):
            raise GeneratorError(
                f"{path}: format 1 lock has a `renames` map; move it to {RENAMES_FILE} "
                f"and remove it from the lock"
            )
        lock["format"] = LOCK_FORMAT
    elif fmt != LOCK_FORMAT:
        raise GeneratorError(f"{path}: unsupported lock format {fmt!r}")
    lock.setdefault("messages", {})
    return lock


def load_renames(path: Path) -> dict[str, dict[str, str]]:
    """Read and validate generator/field-renames.json: {"Message": {"new": "old"}}."""
    try:
        renames = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise GeneratorError(f"{path}: not found (use {{}} when there are no renames)") from None
    except json.JSONDecodeError as exc:
        raise GeneratorError(f"{path}: invalid JSON: {exc}") from None
    validate_renames(renames, str(path))
    return renames


def validate_renames(renames: object, where: str = "renames") -> None:
    if not isinstance(renames, dict):
        raise GeneratorError(f'{where}: expected {{"Message": {{"new_name": "old_name"}}}}')
    for msg, pairs in renames.items():
        if not isinstance(pairs, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in pairs.items()
        ):
            raise GeneratorError(f'{where}: {msg}: expected {{"new_name": "old_name"}}')
        for new, old in pairs.items():
            if new == old:
                raise GeneratorError(f"{where}: {msg}.{new} is renamed to itself")
        olds = list(pairs.values())
        if len(set(olds)) != len(olds):
            raise GeneratorError(f"{where}: {msg}: an old name is listed for two new names")


def dump_lock(lock: dict) -> str:
    out = {"format": lock["format"], "messages": {}}
    for name in sorted(lock["messages"]):
        entry = lock["messages"][name]
        out["messages"][name] = {
            "fields": dict(sorted(entry.get("fields", {}).items(), key=lambda kv: kv[1])),
            "retired": [
                dict(sorted(r.items()))
                for r in sorted(
                    entry.get("retired", []),
                    key=lambda r: (r["number"] is None, r["number"] or 0, r["name"]),
                )
            ],
        }
    return json.dumps(out, indent=2, ensure_ascii=False) + "\n"


def _next_number(used: set[int]) -> int:
    n = max(used, default=0) + 1
    if n in FIRST_RESERVED_RANGE:
        n = FIRST_RESERVED_RANGE.stop
    if n > MAX_FIELD_NUMBER:
        raise GeneratorError("field numbers exhausted")
    return n


def _applied(retired: list[dict], new: str, old: str) -> bool:
    return any(r["name"] == old and r.get("renamed_to") == new for r in retired)


def _rename(msg: str, entry: dict, wanted: list[str], new: str, old: str) -> int:
    """Move old's number to new and keep old reserved by name. Returns the number."""
    fields, retired = entry["fields"], entry["retired"]
    where = f"{RENAMES_FILE}: {msg}.{new} <- {old}"
    if old in wanted:
        raise GeneratorError(f"{where}: the FOM still has {old!r}; remove the entry")
    if new not in wanted:
        raise GeneratorError(f"{where}: the FOM has no field {new!r}; fix or remove the entry")
    numbered = [r for r in retired if r["name"] == old and r["number"] is not None]
    if old in fields:
        number = fields[old]
    elif numbered:
        number = numbered[-1]["number"]
    else:
        raise GeneratorError(f"{where}: the lock has no number for {old!r}; fix or remove the entry")
    if new in fields:
        raise GeneratorError(
            f"{where}: the lock already gives {new!r} number {fields[new]}, so it cannot take "
            f"number {number} from {old!r}. The rename was listed after the generator numbered the "
            f"new name. If number {fields[new]} was never released, revert "
            f"generator/field-ids.lock.json to before it was assigned and regenerate it in the "
            f"same pull request; otherwise remove the entry and keep {fields[new]}."
        )
    if old in fields:
        del fields[old]
    else:
        retired.remove(numbered[-1])
    retired.append({"name": old, "number": None, "renamed_to": new})
    fields[new] = number
    return number


def assign(
    lock: dict, messages: dict[str, list[str]], renames: dict[str, dict[str, str]] | None = None
) -> tuple[dict, Changes]:
    """Return the updated lock and what changed.

    `messages` maps each message name to its field names in FOM order;
    `renames` is the content of generator/field-renames.json.
    """
    renames = renames or {}
    validate_renames(renames)
    lock = copy.deepcopy(lock)
    changes = Changes()
    for msg in sorted(set(renames) - set(messages)):
        retired = lock["messages"].get(msg, {}).get("retired", [])
        pending = [n for n, o in renames[msg].items() if not _applied(retired, n, o)]
        if pending:
            raise GeneratorError(f"{RENAMES_FILE}: {msg}: no such message in the FOM")
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

        for new, old in sorted(renames.get(msg, {}).items()):
            if not _applied(retired, new, old):
                number = _rename(msg, entry, wanted, new, old)
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
