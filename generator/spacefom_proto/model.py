"""Intermediate model of the FOM declarations the generator understands."""

from __future__ import annotations

from dataclasses import dataclass, field


class GeneratorError(Exception):
    """Raised for any input the generator cannot map faithfully."""


@dataclass
class SimpleType:
    name: str
    representation: str
    units: str
    semantics: str


@dataclass
class ArrayType:
    name: str
    element: str
    cardinality: int
    encoding: str
    semantics: str


@dataclass
class Member:
    """A record field, an object-class attribute or an interaction parameter."""

    name: str
    datatype: str
    semantics: str
    inherited_from: str | None = None


@dataclass
class RecordType:
    name: str
    encoding: str
    semantics: str
    fields: list[Member]


@dataclass
class Enumerator:
    name: str
    value: int


@dataclass
class EnumType:
    name: str
    representation: str
    semantics: str
    enumerators: list[Enumerator]


@dataclass
class HlaClass:
    """An object class or interaction class, with its members flattened."""

    kind: str  # "object" or "interaction"
    name: str
    qualified_name: str
    semantics: str
    own_members: list[Member]
    parent: HlaClass | None = None

    @property
    def members(self) -> list[Member]:
        """Inherited members first, in FOM order, then this class's own."""
        inherited = []
        if self.parent is not None:
            for m in self.parent.members:
                inherited.append(
                    Member(m.name, m.datatype, m.semantics, m.inherited_from or self.parent.name)
                )
        return inherited + self.own_members


@dataclass
class Module:
    key: str  # output file stem, e.g. "datatypes"
    filename: str
    sha256: str
    model_name: str
    model_version: str
    # Declarations in FOM document order. Simple types are kept for name
    # resolution but are not emitted as messages.
    declarations: list = field(default_factory=list)
