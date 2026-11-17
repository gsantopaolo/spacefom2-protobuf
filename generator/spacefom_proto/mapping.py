"""Map the FOM model to protobuf messages and enums (docs/technical-overview.md, Mapping)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .model import (
    ArrayType,
    EnumType,
    Enumerator,
    GeneratorError,
    HlaClass,
    Member,
    Module,
    RecordType,
    SimpleType,
)

# HLA datatypes the SpaceFOM modules reference without declaring them (they
# come from the HLA standard MIM). Only the ones in the mapping table.
BUILTIN_SCALARS = {
    "HLAunicodeString": "string",
    "HLAinteger64Time": "int64",
}
SIMPLE_REPRESENTATIONS = {"HLAfloat64LE": "double"}
ENUM_REPRESENTATIONS = {"HLAinteger16LE"}
VECTOR_COMPONENTS = ("x", "y", "z")
MATRIX_CARDINALITY = 9

_MESSAGE_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*$")
_FIELD_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_ENUM_VALUE = re.compile(r"^[A-Z][A-Z0-9_]*$")


@dataclass
class ProtoField:
    name: str
    type: str  # protobuf scalar or message/enum name
    label: str  # "", "optional" or "repeated"
    comment: list[str] = field(default_factory=list)  # FOM semantics, as paragraphs
    trailing: str = ""  # one-line type/unit note
    note: list[str] = field(default_factory=list)  # generator notes, always emitted


@dataclass
class ProtoMessage:
    name: str
    comment: list[str]
    note: list[str]
    fields: list[ProtoField]


@dataclass
class ProtoEnumValue:
    name: str
    number: int
    trailing: str = ""


@dataclass
class ProtoEnum:
    name: str
    comment: list[str]
    note: list[str]
    values: list[ProtoEnumValue]


@dataclass
class ProtoFile:
    module: Module
    imports: list[str]
    items: list  # ProtoMessage | ProtoEnum, in FOM order


def upper_snake(name: str) -> str:
    """MTRMode -> MTR_MODE, ExecutionMode -> EXECUTION_MODE."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.upper()


class Mapper:
    def __init__(self, modules: list[Module], interactions: bool = True):
        self.modules = modules
        self.interactions = interactions
        self.decls: dict[str, tuple[object, Module]] = {}
        for module in modules:
            for decl in module.declarations:
                if decl.name in self.decls or decl.name in BUILTIN_SCALARS:
                    other = self.decls.get(decl.name, (None, None))[1]
                    where = other.filename if other else "the HLA MIM"
                    raise GeneratorError(
                        f"name collision: {decl.name!r} in {module.filename} and {where}"
                    )
                self.decls[decl.name] = (decl, module)

    def map(self) -> list[ProtoFile]:
        return [self._file(m) for m in self.modules]

    def _file(self, module: Module) -> ProtoFile:
        items = []
        for decl in module.declarations:
            if isinstance(decl, SimpleType):
                self._simple_proto_type(decl)  # validate representation
            elif isinstance(decl, ArrayType):
                msg = self._array(decl)
                if msg is not None:
                    items.append(msg)
            elif isinstance(decl, RecordType):
                items.append(self._record(decl))
            elif isinstance(decl, EnumType):
                items.append(self._enum(decl))
            elif isinstance(decl, HlaClass):
                if decl.kind == "interaction" and not self.interactions:
                    continue
                items.append(self._class(decl))
        imports = set()
        for item in items:
            if isinstance(item, ProtoMessage):
                for f in item.fields:
                    dep = self.decls.get(f.type)
                    if dep is not None and dep[1] is not module:
                        imports.add(dep[1].key)
        order = [m.key for m in self.modules]
        return ProtoFile(module, sorted(imports, key=order.index), items)

    # -- datatypes -------------------------------------------------------

    def _simple_proto_type(self, decl: SimpleType) -> str:
        try:
            return SIMPLE_REPRESENTATIONS[decl.representation]
        except KeyError:
            raise GeneratorError(
                f"simple datatype {decl.name}: unsupported representation {decl.representation!r}"
            ) from None

    def _element(self, decl: ArrayType) -> SimpleType:
        element = self._lookup(decl.element, f"array {decl.name}")
        if not isinstance(element, SimpleType):
            raise GeneratorError(f"array {decl.name}: element {decl.element!r} is not a simple datatype")
        self._simple_proto_type(element)
        return element

    def _array(self, decl: ArrayType) -> ProtoMessage | None:
        if decl.encoding != "HLAfixedArray":
            raise GeneratorError(f"array {decl.name}: unsupported encoding {decl.encoding!r}")
        element = self._element(decl)
        if decl.cardinality == MATRIX_CARDINALITY:
            return None  # inlined as repeated double where used, with its semantics
        if decl.cardinality != len(VECTOR_COMPONENTS):
            raise GeneratorError(f"array {decl.name}: unsupported cardinality {decl.cardinality}")
        self._check_message_name(decl.name)
        unit = _unit_note(element)
        fields = [
            ProtoField(c, SIMPLE_REPRESENTATIONS[element.representation], "", trailing=unit)
            for c in VECTOR_COMPONENTS
        ]
        note = [f"HLAfixedArray of {decl.cardinality} x {element.name} ({element.representation})."]
        return ProtoMessage(decl.name, _paragraphs(decl.semantics), note, fields)

    def _record(self, decl: RecordType) -> ProtoMessage:
        if decl.encoding != "HLAfixedRecord":
            raise GeneratorError(f"record {decl.name}: unsupported encoding {decl.encoding!r}")
        self._check_message_name(decl.name)
        fields = [self._field(m, decl.name, optional=False) for m in decl.fields]
        return ProtoMessage(decl.name, _paragraphs(decl.semantics), ["HLAfixedRecord."], fields)

    def _enum(self, decl: EnumType) -> ProtoEnum:
        if decl.representation not in ENUM_REPRESENTATIONS:
            raise GeneratorError(
                f"enum {decl.name}: unsupported representation {decl.representation!r}"
            )
        self._check_message_name(decl.name)
        seen: dict[int, str] = {}
        for e in decl.enumerators:
            if not _ENUM_VALUE.match(e.name):
                raise GeneratorError(f"enum {decl.name}: invalid value name {e.name!r}")
            if e.value in seen:
                raise GeneratorError(
                    f"enum {decl.name}: {e.name} and {seen[e.value]} share value {e.value}"
                )
            seen[e.value] = e.name
        values = [ProtoEnumValue(e.name, e.value) for e in decl.enumerators]
        # proto3 requires the first enum value to be zero.
        zero = [v for v in values if v.number == 0]
        if zero:
            values = zero + [v for v in values if v.number != 0]
        else:
            name = f"{upper_snake(decl.name)}_UNSPECIFIED"
            if name in seen.values():
                raise GeneratorError(f"enum {decl.name}: synthetic zero value {name} collides")
            values.insert(
                0, ProtoEnumValue(name, 0, "Not in the FOM; proto3 requires a zero value.")
            )
        return ProtoEnum(
            decl.name, _paragraphs(decl.semantics), [f"{decl.representation} enumeration."], values
        )

    # -- classes ---------------------------------------------------------

    def _class(self, decl: HlaClass) -> ProtoMessage:
        self._check_message_name(decl.name)
        kind = "Object class" if decl.kind == "object" else "Interaction class"
        note = [f"{kind} {decl.qualified_name}."]
        if decl.parent is not None:
            note.append(
                f"Inherited attributes from {decl.parent.name} come first, in FOM order."
            )
        fields = [
            self._field(m, decl.name, optional=decl.kind == "object") for m in decl.members
        ]
        return ProtoMessage(decl.name, _paragraphs(decl.semantics), note, fields)

    def _field(self, member: Member, owner: str, optional: bool) -> ProtoField:
        if not _FIELD_NAME.match(member.name):
            raise GeneratorError(f"{owner}.{member.name}: not a valid protobuf field name")
        f = self._typed_field(member, owner, optional)
        if member.inherited_from:
            f.note = [f"Inherited from {member.inherited_from}."]
        return f

    def _typed_field(self, member: Member, owner: str, optional: bool) -> ProtoField:
        comment = _paragraphs(member.semantics)
        label = "optional" if optional else ""
        if member.datatype in BUILTIN_SCALARS:
            return ProtoField(
                member.name, BUILTIN_SCALARS[member.datatype], label, comment, member.datatype
            )
        decl = self._lookup(member.datatype, f"{owner}.{member.name}")
        if isinstance(decl, SimpleType):
            return ProtoField(
                member.name, self._simple_proto_type(decl), label, comment,
                f"{decl.name}: {decl.units or 'no units given'}",
            )
        if isinstance(decl, ArrayType) and decl.cardinality == MATRIX_CARDINALITY:
            # The matrix type has no message of its own, so its semantics
            # (element order, sign conventions) go on each field that uses it.
            element = self._element(decl)
            matrix = _paragraphs(decl.semantics)
            if matrix:
                matrix[0] = f"{decl.name}: {matrix[0]}"
            note = f"{decl.name}: 3x3 as 9 elements in HLA array order; {_unit_note(element)}"
            return ProtoField(
                member.name, SIMPLE_REPRESENTATIONS[element.representation], "repeated",
                comment + matrix, note,
            )
        if isinstance(decl, (ArrayType, RecordType, EnumType)):
            return ProtoField(member.name, decl.name, label, comment)
        raise GeneratorError(
            f"{owner}.{member.name}: datatype {member.datatype!r} cannot be used as a field type"
        )

    def _lookup(self, name: str, where: str):
        try:
            return self.decls[name][0]
        except KeyError:
            raise GeneratorError(f"{where}: unknown datatype {name!r}") from None

    @staticmethod
    def _check_message_name(name: str) -> None:
        if not _MESSAGE_NAME.match(name):
            raise GeneratorError(f"{name!r} is not a valid protobuf type name")


def _unit_note(element: SimpleType) -> str:
    return f"{element.name}: {element.units or 'no units given'}"


def _paragraphs(text: str) -> list[str]:
    """Split FOM <semantics> into paragraphs, keeping numbered list items apart.

    Whitespace inside a paragraph is collapsed so the emitter can word-wrap;
    the words themselves are kept verbatim.
    """
    out: list[str] = []
    for block in re.split(r"\n\s*\n", text.strip()):
        current: list[str] = []
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            if re.match(r"^\d+\.\s", line) and current:
                out.append(" ".join(" ".join(current).split()))
                current = []
            current.append(line)
        if current:
            out.append(" ".join(" ".join(current).split()))
    return out
