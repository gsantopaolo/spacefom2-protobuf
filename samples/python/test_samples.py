"""Tests for the generated Python bindings (run: python -m pytest samples/python)."""

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "generated" / "python"))

from google.protobuf.descriptor import FieldDescriptor  # noqa: E402
from google.protobuf.message_factory import GetMessageClass  # noqa: E402

import reader  # noqa: E402
import writer  # noqa: E402
from siso.spacefom.v1 import datatypes_pb2, entity_pb2, environment_pb2, management_pb2  # noqa: E402

MODULES = [datatypes_pb2, environment_pb2, entity_pb2, management_pb2]
EXPECTED_MESSAGES = 18


def all_messages():
    return [m for mod in MODULES for m in mod.DESCRIPTOR.message_types_by_name.values()]


def scalar_value(field):
    if field.type == FieldDescriptor.TYPE_DOUBLE:
        return 1.25
    if field.type == FieldDescriptor.TYPE_INT64:
        return 7
    if field.type == FieldDescriptor.TYPE_STRING:
        return "x"
    if field.type == FieldDescriptor.TYPE_ENUM:
        return field.enum_type.values[-1].number
    raise AssertionError(f"unexpected field type {field.type} in {field.full_name}")


def fill(message):
    """Set every field of message (recursively) to a non-default value."""
    for field in message.DESCRIPTOR.fields:
        if field.type == FieldDescriptor.TYPE_MESSAGE:
            fill(getattr(message, field.name))
        elif field.is_repeated:
            getattr(message, field.name).extend([scalar_value(field)] * 9)
        else:
            setattr(message, field.name, scalar_value(field))


def test_fixture_values():
    assert reader.verify() == 5


def test_fixture_files_are_up_to_date():
    for name, message in writer.build().items():
        committed = (HERE.parent / "data" / f"{name}.binpb").read_bytes()
        assert committed == message.SerializeToString(deterministic=True), name


def test_every_message_type_is_generated():
    names = sorted(m.name for m in all_messages())
    assert len(names) == EXPECTED_MESSAGES, names


@pytest.mark.parametrize("descriptor", all_messages(), ids=lambda d: d.name)
def test_every_message_round_trips_with_all_fields_set(descriptor):
    cls = GetMessageClass(descriptor)
    original = cls()
    fill(original)
    assert len(original.ListFields()) == len(descriptor.fields)
    decoded = cls.FromString(original.SerializeToString())
    assert decoded == original
    assert len(decoded.ListFields()) == len(descriptor.fields)


def test_enums():
    assert [v.number for v in management_pb2.ExecutionMode.DESCRIPTOR.values] == [0, 1, 2, 3, 4]
    assert management_pb2.MTR_MODE_UNSPECIFIED == 0
    assert [v.number for v in management_pb2.MTRMode.DESCRIPTOR.values] == [0, 2, 3, 4]


def test_optional_presence():
    frame = environment_pb2.ReferenceFrame()
    assert not frame.HasField("parent_name")
    frame.parent_name = ""
    assert frame.HasField("parent_name")
    assert environment_pb2.ReferenceFrame.FromString(frame.SerializeToString()).HasField("parent_name")
