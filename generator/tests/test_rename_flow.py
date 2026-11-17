"""The rename flow end to end, through the command line (#29, M1).

main holds a lock. The FOM renames a field. The bot's first run numbers the
new name and asks for review. A reviewer lists the rename in
field-renames.json before the bot's pull request is merged; the bot's next
run, again from main's lock, keeps the old number and reserves the old name.
A rename listed after the bot's pull request was merged fails loudly.
"""

import hashlib
import json
import shutil

import pytest

from helpers import attributes, compile_descriptors, messages, write_module
from spacefom_proto.__main__ import main

ENTITY = "siso/spacefom/v1/entity.proto"
STRING = 9


def entity(*names):
    return (
        "<objects><objectClass><name>HLAobjectRoot</name><objectClass><name>Thing</name>"
        + attributes(*((n, "HLAunicodeString") for n in names))
        + "</objectClass></objectClass></objects>"
    )


class Repo:
    def __init__(self, root):
        self.root = root
        self.fom = root / "fom"
        self.fom.mkdir(parents=True)
        self.lock = root / "lock.json"
        self.renames = root / "renames.json"
        self.renames.write_text("{}\n")

    def set_fom(self, *names):
        path = write_module(self.fom, "entity", entity(*names))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        source = {"files": [{"name": path.name, "sha256": digest}]}
        (self.root / "SOURCE.json").write_text(json.dumps(source))

    def generate(self, out, lock=None):
        report = self.root / f"{out}.md"
        code = main([
            "generate", "--fom-dir", str(self.fom), "--source", str(self.root / "SOURCE.json"),
            "--out", str(self.root / out), "--lock", str(lock or self.lock),
            "--renames", str(self.renames), "--report", str(report),
        ])
        return code, report.read_text() if report.exists() else ""

    def fields(self, out, tmp):
        fds = compile_descriptors(self.root / out, [ENTITY], tmp / f"{out}.pb")
        return messages(fds)["siso.spacefom.v1.Thing"]


@pytest.fixture
def repo(tmp_path):
    r = Repo(tmp_path / "repo")
    r.set_fom("name", "old_name")
    assert r.generate("main")[0] == 0
    return r


def test_rename_listed_before_merge_keeps_number(repo, tmp_path):
    main_lock = repo.lock.read_text()
    repo.set_fom("name", "new_name")

    # First bot run: the new name gets a new number and the PR asks for review.
    code, report = repo.generate("bot1")
    assert code == 0
    assert "### Needs human review" in report and "- `Thing`" in report
    assert "`Thing.new_name` = 3" in report
    assert "generator/field-renames.json" in report
    assert repo.fields("bot1", tmp_path)["new_name"][0] == 3
    bot_lock = repo.lock.read_text()

    # The reviewer lists the rename on main; the bot reruns from main's lock.
    repo.lock.write_text(main_lock)
    repo.renames.write_text(json.dumps({"Thing": {"new_name": "old_name"}}))
    code, report = repo.generate("bot2")
    assert code == 0
    assert "`Thing.old_name` -> `Thing.new_name` keeps 2" in report
    assert "Needs human review" not in report
    assert repo.fields("bot2", tmp_path) == {
        "name": (1, STRING, "", 1, True), "new_name": (2, STRING, "", 1, True),
    }
    text = (repo.root / "bot2" / ENTITY).read_text()
    assert '  reserved "old_name";\n}' in text
    assert "reserved 2" not in text and "reserved 3" not in text

    # Running again changes nothing.
    first = (repo.root / "bot2" / ENTITY).read_text(), repo.lock.read_text()
    assert repo.generate("bot2")[0] == 0
    assert ((repo.root / "bot2" / ENTITY).read_text(), repo.lock.read_text()) == first

    # Too late: the bot's PR, with new_name = 3, was merged first.
    late = repo.root / "late.json"
    late.write_text(bot_lock)
    shutil.rmtree(repo.root / "bot2")
    code, _ = repo.generate("bot2", lock=late)
    assert code == 2
    assert late.read_text() == bot_lock  # nothing written


def test_late_rename_error_says_how_to_fix(repo, capsys):
    repo.set_fom("name", "new_name")
    assert repo.generate("bot1")[0] == 0
    repo.renames.write_text(json.dumps({"Thing": {"new_name": "old_name"}}))
    assert repo.generate("bot1")[0] == 2
    err = capsys.readouterr().err
    assert "already gives 'new_name' number 3, so it cannot take number 2 from 'old_name'" in err
    assert "remove the entry and keep 3" in err
