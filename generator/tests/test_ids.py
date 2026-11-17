import json

import pytest

from spacefom_proto.ids import (
    LOCK_FORMAT,
    assign,
    dump_lock,
    empty_lock,
    load_lock,
    load_renames,
    reserved,
)
from spacefom_proto.model import GeneratorError


def test_first_run_numbers_follow_fom_order():
    lock, changes = assign(empty_lock(), {"M": ["a", "b", "c"]})
    assert lock["messages"]["M"]["fields"] == {"a": 1, "b": 2, "c": 3}
    assert changes.new_messages == ["M"]


def test_inserted_field_gets_next_number_and_others_keep_theirs():
    lock, _ = assign(empty_lock(), {"M": ["a", "b"]})
    lock, changes = assign(lock, {"M": ["new", "a", "b"]})
    assert lock["messages"]["M"]["fields"] == {"a": 1, "b": 2, "new": 3}
    assert changes.added == [("M", "new", 3)]


def test_removed_field_is_reserved_and_never_reused():
    lock, _ = assign(empty_lock(), {"M": ["a", "b", "c"]})
    lock, changes = assign(lock, {"M": ["a", "b"]})
    assert changes.retired == [("M", "c", 3)]
    assert reserved(lock["messages"]["M"]) == ([3], ["c"])
    lock, _ = assign(lock, {"M": ["a", "b", "d"]})
    assert lock["messages"]["M"]["fields"]["d"] == 4


def test_readded_name_gets_new_number_and_is_not_reserved_by_name():
    lock, _ = assign(empty_lock(), {"M": ["a", "b"]})
    lock, _ = assign(lock, {"M": ["a"]})
    lock, _ = assign(lock, {"M": ["a", "b"]})
    assert lock["messages"]["M"]["fields"] == {"a": 1, "b": 3}
    assert reserved(lock["messages"]["M"]) == ([2], [])


def test_rename_without_map_needs_review():
    lock, _ = assign(empty_lock(), {"M": ["a", "old"]})
    lock, changes = assign(lock, {"M": ["a", "new"]})
    assert lock["messages"]["M"]["fields"] == {"a": 1, "new": 3}
    assert changes.needs_review() == ["M"]


def test_rename_of_live_field_keeps_number_and_reserves_old_name():
    lock, _ = assign(empty_lock(), {"M": ["a", "old"]})
    lock, changes = assign(lock, {"M": ["a", "new"]}, {"M": {"new": "old"}})
    assert lock["messages"]["M"]["fields"] == {"a": 1, "new": 2}
    assert changes.renamed == [("M", "old", "new", 2)]
    assert changes.added == [] and changes.retired == []
    assert changes.needs_review() == []
    assert reserved(lock["messages"]["M"]) == ([], ["old"])


def test_rename_of_retired_field_keeps_number_and_reserves_old_name():
    lock, _ = assign(empty_lock(), {"M": ["a", "old"]})
    lock, _ = assign(lock, {"M": ["a"]})
    lock, changes = assign(lock, {"M": ["a", "new"]}, {"M": {"new": "old"}})
    assert lock["messages"]["M"]["fields"]["new"] == 2
    assert changes.renamed == [("M", "old", "new", 2)]
    assert reserved(lock["messages"]["M"]) == ([], ["old"])


def test_applied_rename_is_skipped_on_later_runs():
    renames = {"M": {"new": "old"}}
    lock, _ = assign(empty_lock(), {"M": ["a", "old"]})
    lock, _ = assign(lock, {"M": ["a", "new"]}, renames)
    again, changes = assign(lock, {"M": ["a", "new"]}, renames)
    assert again == lock and changes.empty()
    # A later rename of the new name chains on; the first entry stays history.
    renames["M"]["newer"] = "new"
    lock, changes = assign(lock, {"M": ["a", "newer"]}, renames)
    assert lock["messages"]["M"]["fields"] == {"a": 1, "newer": 2}
    assert changes.renamed == [("M", "new", "newer", 2)]
    assert reserved(lock["messages"]["M"]) == ([], ["new", "old"])


def test_rename_fails_when_new_name_already_has_a_number():
    lock, _ = assign(empty_lock(), {"M": ["a", "old"]})
    lock, _ = assign(lock, {"M": ["a", "new"]})  # new = 3, old retired at 2
    message = "already gives 'new' number 3, so it cannot take number 2 from 'old'"
    with pytest.raises(GeneratorError, match=message):
        assign(lock, {"M": ["a", "new"]}, {"M": {"new": "old"}})


@pytest.mark.parametrize(
    "renames, fields, message",
    [
        ({"M": {"new": "nope"}}, ["a", "new"], "no number for 'nope'"),
        ({"M": {"new": "old"}}, ["a", "old", "new"], "still has 'old'"),
        ({"M": {"gone": "old"}}, ["a"], "has no field 'gone'"),
        ({"X": {"new": "old"}}, ["a", "old"], "X: no such message"),
        ({"M": {"x": "x"}}, ["a", "old"], "renamed to itself"),
        ({"M": {"x": "old", "y": "old"}}, ["a", "old"], "listed for two new names"),
        ({"M": ["new", "old"]}, ["a", "old"], "expected"),
    ],
)
def test_bad_rename_fails_loudly(renames, fields, message):
    lock, _ = assign(empty_lock(), {"M": ["a", "old"]})
    with pytest.raises(GeneratorError, match=message):
        assign(lock, {"M": fields}, renames)


def test_load_renames(tmp_path):
    path = tmp_path / "renames.json"
    path.write_text('{"M": {"new": "old"}}')
    assert load_renames(path) == {"M": {"new": "old"}}
    with pytest.raises(GeneratorError, match="not found"):
        load_renames(tmp_path / "missing.json")
    path.write_text("{")
    with pytest.raises(GeneratorError, match="invalid JSON"):
        load_renames(path)
    path.write_text("[]")
    with pytest.raises(GeneratorError, match="expected"):
        load_renames(path)


def test_format_1_lock_is_migrated(tmp_path):
    path = tmp_path / "lock.json"
    path.write_text(json.dumps({"format": 1, "messages": {"M": {"fields": {"a": 1}, "retired": []}},
                                "renames": {}}))
    lock = load_lock(path)
    assert lock == {"format": LOCK_FORMAT, "messages": {"M": {"fields": {"a": 1}, "retired": []}}}
    assert '"renames"' not in dump_lock(lock)


def test_format_1_lock_with_renames_must_move_them(tmp_path):
    path = tmp_path / "lock.json"
    path.write_text(json.dumps({"format": 1, "messages": {}, "renames": {"M": {"new": "old"}}}))
    with pytest.raises(GeneratorError, match="move it to generator/field-renames.json"):
        load_lock(path)


def test_unknown_lock_format_fails(tmp_path):
    path = tmp_path / "lock.json"
    path.write_text(json.dumps({"format": 99, "messages": {}}))
    with pytest.raises(GeneratorError, match="unsupported lock format 99"):
        load_lock(path)


def test_skips_implementation_reserved_range():
    lock = empty_lock()
    lock["messages"]["M"] = {"fields": {"a": 18999}, "retired": []}
    lock, _ = assign(lock, {"M": ["a", "b"]})
    assert lock["messages"]["M"]["fields"]["b"] == 20000


def test_removed_message_retires_all_fields():
    lock, _ = assign(empty_lock(), {"M": ["a"], "N": ["b"]})
    lock, changes = assign(lock, {"M": ["a"]})
    assert changes.removed_messages == ["N"]
    assert reserved(lock["messages"]["N"]) == ([1], ["b"])


def test_dump_is_stable_and_idempotent():
    lock, _ = assign(empty_lock(), {"Z": ["b", "a"], "A": ["x"]})
    text = dump_lock(lock)
    assert list(json.loads(text)["messages"]) == ["A", "Z"]
    again, changes = assign(json.loads(text), {"Z": ["b", "a"], "A": ["x"]})
    assert dump_lock(again) == text and changes.empty()
