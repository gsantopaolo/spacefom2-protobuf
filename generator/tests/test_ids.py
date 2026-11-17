import json

from spacefom_proto.ids import assign, dump_lock, empty_lock, reserved


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


def test_rename_map_keeps_number():
    lock, _ = assign(empty_lock(), {"M": ["a", "old"]})
    lock["renames"] = {"M": {"new": "old"}}
    lock, changes = assign(lock, {"M": ["a", "new"]})
    assert lock["messages"]["M"]["fields"] == {"a": 1, "new": 2}
    assert changes.renamed == [("M", "old", "new", 2)]
    assert changes.needs_review() == []
    # Applied after the fact (old already retired): still keeps the number,
    # and the old name stays reserved.
    lock2, _ = assign(empty_lock(), {"M": ["a", "old"]})
    lock2, _ = assign(lock2, {"M": ["a"]})
    lock2["renames"] = {"M": {"new": "old"}}
    lock2, _ = assign(lock2, {"M": ["a", "new"]})
    assert lock2["messages"]["M"]["fields"]["new"] == 2
    assert reserved(lock2["messages"]["M"]) == ([], ["old"])


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
