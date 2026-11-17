"""The Markdown report that becomes the bot's pull request body."""

from spacefom_proto.generate import report
from spacefom_proto.ids import RENAMES_FILE, Changes


def test_nothing_changed():
    assert report(Changes()) == "## Field number changes\n\nNo field numbers changed.\n"


def test_new_messages_only_list_the_messages():
    text = report(Changes(added=[("M", "a", 1)], new_messages=["M"]))
    assert text == "## Field number changes\n\nNew messages: `M`\n"


def test_every_section():
    changes = Changes(
        added=[("A", "b", 3), ("New", "x", 1)],
        retired=[("A", "c", 2), ("Gone", "y", 1)],
        renamed=[("R", "old", "new", 4)],
        new_messages=["New"],
        removed_messages=["Gone"],
    )
    assert report(changes) == (
        "## Field number changes\n"
        "\n"
        "New messages: `New`\n"
        "\n"
        "### Added fields\n\n- `A.b` = 3\n\n"
        "### Retired fields (now `reserved`)\n\n- `A.c` was 2\n- `Gone.y` was 1\n\n"
        f"### Renamed fields (from `{RENAMES_FILE}`)\n\n- `R.old` -> `R.new` keeps 4\n\n"
        "### Removed messages\n\n- `Gone`\n\n"
        "### Needs human review\n"
        "\n"
        "These messages gained and lost fields in the same run. If a field was renamed, "
        f"add it to `{RENAMES_FILE}` as "
        '`{"Message": {"new_name": "old_name"}}` in a pull request to `main`, and merge '
        "that pull request before this one. The bot then regenerates this pull request and "
        "the new name keeps the old number. After this pull request is merged, the new "
        "number is in the lock and the rename can no longer be applied.\n"
        "\n"
        "- `A`\n"
    )


def test_review_is_not_asked_for_added_or_retired_alone():
    text = report(Changes(added=[("A", "b", 3)], retired=[("B", "c", 2)]))
    assert "Needs human review" not in text
