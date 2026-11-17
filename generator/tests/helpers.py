"""Build small IEEE 1516-2010 DIF fixture modules and compile .proto text."""

from __future__ import annotations

import textwrap
from pathlib import Path

from google.protobuf import descriptor_pb2
from grpc_tools import protoc


def fom(body: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">\n'
        "<modelIdentification><name>Test</name><version>1.0</version></modelIdentification>\n"
        + textwrap.dedent(body)
        + "\n</objectModel>\n"
    )


def write_module(directory: Path, key: str, body: str) -> Path:
    path = directory / f"SISO_SpaceFOM_{key}.xml"
    path.write_text(fom(body), encoding="utf-8")
    return path


def simple(name: str, units: str = "meter (m)", rep: str = "HLAfloat64LE") -> str:
    return (
        f"<simpleData><name>{name}</name><representation>{rep}</representation>"
        f"<units>{units}</units><semantics>{name} semantics.</semantics></simpleData>"
    )


def attributes(*pairs: tuple[str, str]) -> str:
    return "".join(
        f"<attribute><name>{n}</name><dataType>{t}</dataType><semantics>{n}.</semantics></attribute>"
        for n, t in pairs
    )


def compile_descriptors(root: Path, files: list[str], out: Path) -> descriptor_pb2.FileDescriptorSet:
    """Compile with the protoc bundled in grpcio-tools; no source info, so no comments."""
    rc = protoc.main(["protoc", f"-I{root}", f"--descriptor_set_out={out}", *files])
    if rc != 0:
        raise AssertionError(f"protoc failed ({rc}) on {files}")
    fds = descriptor_pb2.FileDescriptorSet()
    fds.ParseFromString(out.read_bytes())
    return fds


def messages(fds: descriptor_pb2.FileDescriptorSet) -> dict:
    out = {}
    for f in fds.file:
        for m in f.message_type:
            out[f"{f.package}.{m.name}"] = {
                fd.name: (fd.number, fd.type, fd.type_name, fd.label, fd.proto3_optional)
                for fd in m.field
            }
    return out
