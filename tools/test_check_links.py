"""Tests for check_links.py (run: python -m pytest tools)."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_links import anchors, check_file, link_targets, main, slugify  # noqa: E402


@pytest.mark.parametrize(
    ("heading", "slug"),
    [
        ("Ground rules", "ground-rules"),
        ("Part 1: test the generator", "part-1-test-the-generator"),
        ("M2. buf is not pinned", "m2-buf-is-not-pinned"),
        ("SpaceFOM ⇄ Protobuf", "spacefom--protobuf"),
        ("What `buf breaking` checks", "what-buf-breaking-checks"),
        ("snake_case stays", "snake_case-stays"),
        ("Plan §6, step 6", "plan-6-step-6"),
        ("Ünïcode Letters", "ünïcode-letters"),
        ("A -- B", "a----b"),
    ],
)
def test_slug_follows_github(heading, slug):
    assert slugify(heading) == slug


def test_anchors_from_rendered_heading_text():
    text = "# The `fetch` step\n\n## See [the plan](plan.md)\n\n### **Bold** and _em_\n"
    assert anchors(text) == {"the-fetch-step", "see-the-plan", "bold-and-em"}


def test_repeated_headings_are_numbered():
    text = "# Notes\n\n## Notes\n\n### Notes\n"
    assert anchors(text) == {"notes", "notes-1", "notes-2"}


def test_setext_headings_and_closing_hashes():
    text = "Title\n=====\n\nSub\n---\n\n## Closed ##\n"
    assert anchors(text) == {"title", "sub", "closed"}


def test_list_item_above_a_rule_is_not_a_heading():
    assert anchors("- item\n---\n") == set()


def test_explicit_html_ids_and_names():
    text = '<a id="custom"></a>\n<span name="old-name">x</span>\n'
    assert anchors(text) == {"custom", "old-name"}


def test_headings_in_code_blocks_and_comments_are_ignored():
    text = "```\n# not a heading\n```\n<!--\n# hidden\n-->\n~~~~\n## nor this\n~~~~\n# Real\n"
    assert anchors(text) == {"real"}


def test_link_targets_with_line_numbers():
    text = (
        "Intro [a](a.md) and ![img](img/x.png).\n"
        "Second [b](<with space.md> \"title\") line.\n"
        "[ref]: docs/ref.md#part\n"
        '<a href="html.md">x</a>\n'
    )
    assert link_targets(text) == [
        (1, "a.md"),
        (1, "img/x.png"),
        (2, "with space.md"),
        (3, "docs/ref.md#part"),
        (4, "html.md"),
    ]


def test_links_in_code_are_ignored():
    text = "`[x](missing.md)`\n\n```md\n[y](missing.md)\n```\n<!-- [z](missing.md) -->\n"
    assert link_targets(text) == []


def test_link_with_parentheses_in_target():
    assert link_targets("[w](wiki/Foo_(bar).md)") == [(1, "wiki/Foo_(bar).md")]


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("# Guide\n\n## Step one\n\n## Step one\n")
    (tmp_path / "docs" / "space name.md").write_text("# Spaced\n")
    (tmp_path / "src.py").write_text("print()\n")
    return tmp_path


def write(repo, text):
    md = repo / "README.md"
    md.write_text(text)
    return check_file(md, repo)


def test_valid_links_pass(repo):
    text = (
        "[g](docs/guide.md) [s](docs/guide.md#step-one-1) [self](#top) [dir](docs/)\n"
        "[root](/docs/guide.md#guide) [enc](docs/space%20name.md#spaced) [code](src.py#L1)\n"
        "[web](https://example.com/missing) [mail](mailto:a@b.c) [proto](//example.com)\n"
        "# Top\n"
    )
    assert write(repo, text) == []


def test_missing_file_is_reported(repo):
    (broken,) = write(repo, "line one\n[x](docs/nope.md)\n")
    assert (str(broken.file), broken.line, broken.target) == ("README.md", 2, "docs/nope.md")
    assert broken.reason == "no such file or folder"


def test_missing_anchor_is_reported(repo):
    (broken,) = write(repo, "[x](docs/guide.md#step-two)\n")
    assert "no heading or id #step-two in docs/guide.md" in broken.reason


def test_missing_anchor_in_same_file_is_reported(repo):
    (broken,) = write(repo, "# Title\n\n[x](#titel)\n")
    assert broken.line == 3


def test_anchor_match_is_case_sensitive(repo):
    assert len(write(repo, "[x](docs/guide.md#Guide)\n")) == 1


def test_link_outside_repository_is_reported(repo):
    (broken,) = write(repo, "[x](../outside.md)\n")
    assert broken.reason == "points outside the repository"


def test_main_checks_tracked_files_and_exit_code(repo, capsys):
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "README.md").write_text("[ok](docs/guide.md)\n")
    (repo / "untracked.md").write_text("[bad](nope.md)\n")
    subprocess.run(["git", "-C", str(repo), "add", "README.md", "docs"], check=True)
    assert main(["--root", str(repo)]) == 0

    subprocess.run(["git", "-C", str(repo), "add", "untracked.md"], check=True)
    assert main(["--root", str(repo)]) == 1
    assert "untracked.md:1: nope.md: no such file or folder" in capsys.readouterr().out


def test_superscript_numbers_are_dropped():
    assert slugify("Area in m²") == "area-in-m"


def test_dedup_skips_a_slug_already_taken():
    # github-slugger: "a", then "a-1" (a real heading), then "a" again becomes "a-2".
    assert anchors("# a\n# a-1\n# a\n") == {"a", "a-1", "a-2"}


def test_footnote_definitions_are_not_links():
    assert link_targets("Text[^1].\n\n[^1]: A note, not a path.\n") == []
