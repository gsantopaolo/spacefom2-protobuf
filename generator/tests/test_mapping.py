import pytest

from helpers import attributes, compile_descriptors, messages, simple, write_module
from spacefom_proto.generate import generate
from spacefom_proto.ids import empty_lock
from spacefom_proto.mapping import _paragraphs, upper_snake
from spacefom_proto.model import GeneratorError

DATATYPES = f"""
<dataTypes>
  <simpleDataTypes>{simple("Length")}{simple("Inertia", "kilogram meter squared (kg*m^2)")}</simpleDataTypes>
  <enumeratedDataTypes>
    <enumeratedData><name>MTRMode</name><representation>HLAinteger16LE</representation>
      <semantics>Requests.</semantics>
      <enumerator><name>MTR_GOTO_RUN</name><value>2</value></enumerator>
      <enumerator><name>MTR_GOTO_FREEZE</name><value>3</value></enumerator>
    </enumeratedData>
    <enumeratedData><name>ExecutionMode</name><representation>HLAinteger16LE</representation>
      <enumerator><name>EXEC_MODE_RUNNING</name><value>2</value></enumerator>
      <enumerator><name>EXEC_MODE_UNINITIALIZED</name><value>0</value></enumerator>
    </enumeratedData>
  </enumeratedDataTypes>
  <arrayDataTypes>
    <arrayData><name>PositionVector</name><dataType>Length</dataType><cardinality>3</cardinality>
      <encoding>HLAfixedArray</encoding><semantics>A position.</semantics></arrayData>
    <arrayData><name>InertiaMatrix</name><dataType>Inertia</dataType><cardinality>9</cardinality>
      <encoding>HLAfixedArray</encoding></arrayData>
  </arrayDataTypes>
  <fixedRecordDataTypes>
    <fixedRecordData><name>State</name><encoding>HLAfixedRecord</encoding>
      <field><name>position</name><dataType>PositionVector</dataType></field>
      <field><name>length</name><dataType>Length</dataType></field>
    </fixedRecordData>
  </fixedRecordDataTypes>
</dataTypes>
"""

ENTITY = f"""
<objects><objectClass><name>HLAobjectRoot</name>
  <objectClass><name>Base</name><semantics>Base class.</semantics>
    {attributes(("name", "HLAunicodeString"), ("state", "State"))}
    <objectClass><name>Derived</name>
      {attributes(("inertia", "InertiaMatrix"), ("mode", "ExecutionMode"), ("ticks", "HLAinteger64Time"))}
    </objectClass>
  </objectClass>
</objectClass></objects>
<interactions><interactionClass><name>HLAinteractionRoot</name>
  <interactionClass><name>Request</name>
    <parameter><name>execution_mode</name><dataType>MTRMode</dataType></parameter>
  </interactionClass>
</interactionClass></interactions>
"""


@pytest.fixture
def fom_dir(tmp_path):
    d = tmp_path / "fom"
    d.mkdir()
    write_module(d, "datatypes", DATATYPES)
    write_module(d, "entity", ENTITY)
    return d


def paths(d):
    return [d / "SISO_SpaceFOM_datatypes.xml", d / "SISO_SpaceFOM_entity.xml"]


def compiled(tmp_path, result):
    root = tmp_path / "out"
    for rel, text in result.files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    return messages(compile_descriptors(root, sorted(result.files), tmp_path / "out.pb"))


OPT = 3  # FieldDescriptorProto.LABEL_OPTIONAL
REP = 3
DOUBLE, STRING, INT64, MESSAGE, ENUM = 1, 9, 3, 11, 14


def test_full_mapping_compiles(tmp_path, fom_dir):
    result = generate(paths(fom_dir), empty_lock())
    msgs = compiled(tmp_path, result)
    p = "siso.spacefom.v1."
    assert msgs[p + "PositionVector"] == {
        "x": (1, DOUBLE, "", 1, False), "y": (2, DOUBLE, "", 1, False), "z": (3, DOUBLE, "", 1, False),
    }
    # Fixed records: plain fields, FOM order.
    assert msgs[p + "State"] == {
        "position": (1, MESSAGE, ".siso.spacefom.v1.PositionVector", 1, False),
        "length": (2, DOUBLE, "", 1, False),
    }
    # Object classes: all attributes optional, inherited ones first.
    derived = msgs[p + "Derived"]
    assert [n for n, _ in sorted(derived.items(), key=lambda kv: kv[1][0])] == [
        "name", "state", "inertia", "mode", "ticks",
    ]
    assert derived["name"] == (1, STRING, "", 1, True)
    assert derived["inertia"] == (3, DOUBLE, "", REP, False)  # 9-array -> repeated double
    assert derived["mode"] == (4, ENUM, ".siso.spacefom.v1.ExecutionMode", 1, True)
    assert derived["ticks"] == (5, INT64, "", 1, True)
    # Interactions: plain fields.
    assert msgs[p + "Request"]["execution_mode"][3:] == (1, False)
    assert "InertiaMatrix" not in {k.rsplit(".", 1)[1] for k in msgs}


def test_enum_zero_values(fom_dir):
    text = generate(paths(fom_dir), empty_lock()).files["siso/spacefom/v1/datatypes.proto"]
    assert "enum MTRMode {\n  MTR_MODE_UNSPECIFIED = 0;  // Not in the FOM" in text
    # An existing zero value is moved first instead of adding a synthetic one.
    assert "enum ExecutionMode {\n  EXEC_MODE_UNINITIALIZED = 0;\n  EXEC_MODE_RUNNING = 2;\n}" in text


def test_imports_and_header(fom_dir):
    files = generate(paths(fom_dir), empty_lock()).files
    entity = files["siso/spacefom/v1/entity.proto"]
    assert 'import "siso/spacefom/v1/datatypes.proto";' in entity
    for text in files.values():
        assert "// Reprinted with permission from SISO Inc.\n" in text
        assert "// Code generated by spacefom_proto " in text
        assert "// Source sha256: " in text


def test_semantics_flag(fom_dir):
    on = generate(paths(fom_dir), empty_lock()).files["siso/spacefom/v1/entity.proto"]
    off = generate(paths(fom_dir), empty_lock(), semantics=False).files["siso/spacefom/v1/entity.proto"]
    assert "// Base class." in on and "Base class." not in off
    assert "semantics=off" in off
    assert "Reprinted with permission from SISO Inc." in off
    assert "// Inherited from Base." in off  # generator notes stay


def test_interactions_flag_keeps_numbers(fom_dir):
    result = generate(paths(fom_dir), empty_lock(), interactions=False)
    assert "message Request" not in result.files["siso/spacefom/v1/entity.proto"]
    assert result.lock["messages"]["Request"]["fields"] == {"execution_mode": 1}


@pytest.mark.parametrize(
    "body, message",
    [
        (f"<objects><objectClass><name>HLAobjectRoot</name><objectClass><name>A</name>"
         f"{attributes(('x', 'Nope'))}</objectClass></objectClass></objects>", "unknown datatype"),
        (f"<dataTypes><simpleDataTypes>{simple('L', rep='HLAfloat32BE')}</simpleDataTypes></dataTypes>",
         "unsupported representation"),
        ("<dataTypes><variantRecordDataTypes><variantRecordData><name>V</name></variantRecordData>"
         "</variantRecordDataTypes></dataTypes>", "not supported"),
        (f"<dataTypes><simpleDataTypes>{simple('Length')}</simpleDataTypes></dataTypes>", "name collision"),
        (f"<dataTypes><arrayDataTypes><arrayData><name>V4</name><dataType>Length</dataType>"
         f"<cardinality>4</cardinality><encoding>HLAfixedArray</encoding></arrayData>"
         f"</arrayDataTypes></dataTypes>", "unsupported cardinality"),
    ],
)
def test_fails_loudly(fom_dir, body, message):
    extra = write_module(fom_dir, "extra", body)
    with pytest.raises(GeneratorError, match=message):
        generate([fom_dir / "SISO_SpaceFOM_datatypes.xml", extra], empty_lock())


def test_paragraphs_keep_lists_and_collapse_whitespace():
    text = "Intro  line\n continues:\n1. a -> b \n2. c\n \nSecond   para."
    assert _paragraphs(text) == ["Intro line continues:", "1. a -> b", "2. c", "Second para."]


def test_upper_snake():
    assert upper_snake("MTRMode") == "MTR_MODE"
    assert upper_snake("ExecutionMode") == "EXECUTION_MODE"
