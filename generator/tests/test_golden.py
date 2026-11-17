"""Golden, compile and idempotence tests against the real SpaceFOM modules."""

import json
import os
from pathlib import Path

import pytest

from conftest import REPO
from helpers import compile_descriptors, messages
from spacefom_proto.generate import generate, load_source, verify_inputs
from spacefom_proto.ids import load_lock

PROTO = REPO / "proto"
LOCK = REPO / "generator" / "field-ids.lock.json"
SOURCE = REPO / "fom" / "SOURCE.json"
EXAMPLE = REPO / "docs" / "examples" / "reference_frame.proto"


def committed_protos():
    return sorted(p.relative_to(PROTO).as_posix() for p in PROTO.rglob("*.proto"))


def test_committed_output_compiles(tmp_path):
    assert committed_protos(), "proto/ is empty"
    compile_descriptors(PROTO, committed_protos(), tmp_path / "gen.pb")


def test_golden_example_matches_generated(tmp_path):
    """Every message in the hand-written example exists in the generated output
    with the same field names, numbers, types and labels (plan §5.3)."""
    example = messages(compile_descriptors(EXAMPLE.parent, [EXAMPLE.name], tmp_path / "ex.pb"))
    generated = messages(compile_descriptors(PROTO, committed_protos(), tmp_path / "gen.pb"))
    assert example
    for name, fields in example.items():
        assert name in generated, f"{name} missing from generated output"
        assert generated[name] == fields, name


def fom_dir() -> Path | None:
    candidates = [os.environ.get("SPACEFOM_FOM_DIR"), REPO / "build" / "fom",
                  REPO / "reference-docs" / "standards" / "fom-xml-trickhla"]
    for c in candidates:
        if c and (Path(c) / "SISO_SpaceFOM_datatypes.xml").is_file():
            return Path(c)
    if os.environ.get("SPACEFOM_REQUIRE_FOM"):
        pytest.fail("FOM modules not found; run `python -m spacefom_proto fetch --dest build/fom`")
    pytest.skip("FOM modules not available")


def test_regeneration_is_byte_identical_and_idempotent():
    paths = verify_inputs(fom_dir(), load_source(SOURCE))
    first = generate(paths, load_lock(LOCK))
    second = generate(paths, json.loads(first.lock_text))
    assert first.files == second.files
    assert first.lock_text == second.lock_text
    assert second.changes.empty() and not second.changes.new_messages
    # Whether the committed proto/ matches is decided by the workflow
    # (tools/generated_output_check.py): a PR may change the generator and
    # leave proto/ for the bot to regenerate after the merge (#19).
