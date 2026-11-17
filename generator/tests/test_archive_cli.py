import json
import shutil
from datetime import datetime, timezone

from conftest import REPO
from helpers import write_module
from spacefom_proto.__main__ import main
from spacefom_proto.archive import archive


def test_archive_copies_previous_tree(tmp_path):
    proto = tmp_path / "proto"
    shutil.copytree(REPO / "proto", proto)
    when = datetime(2026, 11, 17, 12, 0, 0, tzinfo=timezone.utc)
    target = archive(proto, tmp_path / "history", "abc123", now=when)
    assert target.name.startswith("20261117T120000Z_")
    assert (target / "proto" / "siso/spacefom/v1/datatypes.proto").is_file()
    manifest = json.loads((target / "MANIFEST.json").read_text())
    assert manifest["main_commit"] == "abc123"
    assert "SISO_SpaceFOM_datatypes.xml" in manifest["fom_sha256"]


def test_archive_nothing(tmp_path):
    assert archive(tmp_path, tmp_path / "history", "x") is None


def test_cli_check_and_write(tmp_path, capsys):
    fom = tmp_path / "fom"
    fom.mkdir()
    path = write_module(fom, "datatypes", "<dataTypes/>")
    import hashlib
    source = tmp_path / "SOURCE.json"
    source.write_text(json.dumps({"files": [
        {"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}]}))
    renames = tmp_path / "renames.json"
    renames.write_text("{}")
    args = ["generate", "--fom-dir", str(fom), "--source", str(source),
            "--out", str(tmp_path / "proto"), "--lock", str(tmp_path / "lock.json"),
            "--renames", str(renames)]
    assert main(args + ["--check"]) == 1
    assert main(args) == 0
    assert main(args + ["--check"]) == 0
    # A tampered input fails the sha256 check.
    path.write_text(path.read_text() + " ")
    assert main(args) == 2
    assert "does not match" in capsys.readouterr().err
