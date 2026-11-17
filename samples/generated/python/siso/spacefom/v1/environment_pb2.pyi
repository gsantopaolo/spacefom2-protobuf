from siso.spacefom.v1 import datatypes_pb2 as _datatypes_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReferenceFrame(_message.Message):
    __slots__ = ("name", "parent_name", "state")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    name: str
    parent_name: str
    state: _datatypes_pb2.SpaceTimeCoordinateState
    def __init__(self, name: _Optional[str] = ..., parent_name: _Optional[str] = ..., state: _Optional[_Union[_datatypes_pb2.SpaceTimeCoordinateState, _Mapping]] = ...) -> None: ...
