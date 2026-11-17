"""Parse IEEE 1516-2010 DIF XML FOM modules into the intermediate model."""

from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path

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

NS = "http://standards.ieee.org/IEEE1516-2010"
_Q = "{%s}" % NS

ROOT_CLASSES = {"HLAobjectRoot", "HLAinteractionRoot"}
_MODULE_FILE = re.compile(r"^SISO_SpaceFOM_(?P<key>[a-z0-9]+)\.xml$")


def _text(elem: ET.Element | None, tag: str) -> str:
    child = elem.find(_Q + tag) if elem is not None else None
    return (child.text or "") if child is not None else ""


def _required(elem: ET.Element, tag: str, where: str) -> str:
    value = _text(elem, tag).strip()
    if not value:
        raise GeneratorError(f"{where}: missing <{tag}>")
    return value


def module_key(filename: str) -> str:
    m = _MODULE_FILE.match(filename)
    if not m:
        raise GeneratorError(f"unexpected FOM module file name: {filename}")
    return m.group("key")


def parse_module(path: Path) -> Module:
    data = path.read_bytes()
    root = ET.fromstring(data)
    if root.tag != _Q + "objectModel":
        raise GeneratorError(f"{path.name}: root element is not an IEEE 1516-2010 objectModel")
    ident = root.find(_Q + "modelIdentification")
    module = Module(
        key=module_key(path.name),
        filename=path.name,
        sha256=hashlib.sha256(data).hexdigest(),
        model_name=_text(ident, "name").strip(),
        model_version=_text(ident, "version").strip(),
    )

    for variant in root.iter(_Q + "variantRecordData"):
        raise GeneratorError(
            f"{path.name}: variant record {_text(variant, 'name')!r} is not supported yet"
        )

    # Walk the top-level sections in document order, so declarations (and the
    # numbers first assigned to their fields) follow the FOM.
    for section in root:
        tag = _local(section.tag)
        if tag == "dataTypes":
            for group in section:
                for elem in group:
                    _datatype(elem, module, path.name)
        elif tag == "objects":
            for top in section.findall(_Q + "objectClass"):
                _classes(top, "object", "objectClass", "attribute", None, "", module, path.name)
        elif tag == "interactions":
            for top in section.findall(_Q + "interactionClass"):
                _classes(
                    top, "interaction", "interactionClass", "parameter", None, "", module, path.name
                )
    return module


def _local(tag) -> str:
    return tag[len(_Q):] if isinstance(tag, str) and tag.startswith(_Q) else str(tag)


def _datatype(elem: ET.Element, module: Module, where: str) -> None:
    tag = _local(elem.tag)
    if tag == "simpleData":
        module.declarations.append(_simple(elem, where))
    elif tag == "arrayData":
        module.declarations.append(_array(elem, where))
    elif tag == "fixedRecordData":
        module.declarations.append(_record(elem, where))
    elif tag == "enumeratedData":
        module.declarations.append(_enum(elem, where))
    elif tag in ("basicData", "variantRecordData"):
        raise GeneratorError(f"{where}: <{tag}> {_text(elem, 'name')!r} is not supported yet")


def _simple(elem: ET.Element, where: str) -> SimpleType:
    name = _required(elem, "name", where)
    return SimpleType(
        name=name,
        representation=_required(elem, "representation", f"{where}: {name}"),
        units=_text(elem, "units").strip(),
        semantics=_text(elem, "semantics"),
    )


def _array(elem: ET.Element, where: str) -> ArrayType:
    name = _required(elem, "name", where)
    cardinality = _required(elem, "cardinality", f"{where}: {name}")
    if not cardinality.isdigit():
        raise GeneratorError(f"{where}: {name}: unsupported cardinality {cardinality!r}")
    return ArrayType(
        name=name,
        element=_required(elem, "dataType", f"{where}: {name}"),
        cardinality=int(cardinality),
        encoding=_required(elem, "encoding", f"{where}: {name}"),
        semantics=_text(elem, "semantics"),
    )


def _record(elem: ET.Element, where: str) -> RecordType:
    name = _required(elem, "name", where)
    return RecordType(
        name=name,
        encoding=_required(elem, "encoding", f"{where}: {name}"),
        semantics=_text(elem, "semantics"),
        fields=[_member(f, f"{where}: {name}") for f in elem.findall(_Q + "field")],
    )


def _enum(elem: ET.Element, where: str) -> EnumType:
    name = _required(elem, "name", where)
    enumerators = []
    for e in elem.findall(_Q + "enumerator"):
        ename = _required(e, "name", f"{where}: {name}")
        value = _required(e, "value", f"{where}: {name}.{ename}")
        try:
            enumerators.append(Enumerator(ename, int(value)))
        except ValueError:
            raise GeneratorError(f"{where}: {name}.{ename}: non-integer value {value!r}") from None
    return EnumType(
        name=name,
        representation=_required(elem, "representation", f"{where}: {name}"),
        semantics=_text(elem, "semantics"),
        enumerators=enumerators,
    )


def _member(elem: ET.Element, where: str) -> Member:
    name = _required(elem, "name", where)
    return Member(
        name=name,
        datatype=_required(elem, "dataType", f"{where}.{name}"),
        semantics=_text(elem, "semantics"),
    )


def _classes(elem, kind, tag, member_tag, parent, prefix, module, where):
    name = _required(elem, "name", where)
    qualified = f"{prefix}.{name}" if prefix else name
    members = [_member(m, f"{where}: {qualified}") for m in elem.findall(_Q + member_tag)]
    current = None
    if name in ROOT_CLASSES:
        if members:
            raise GeneratorError(f"{where}: {name} declares members; not supported")
    else:
        current = HlaClass(kind, name, qualified, _text(elem, "semantics"), members, parent)
        module.declarations.append(current)
    for child in elem.findall(_Q + tag):
        _classes(child, kind, tag, member_tag, current, qualified, module, where)
