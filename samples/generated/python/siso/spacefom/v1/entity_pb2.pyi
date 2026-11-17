from siso.spacefom.v1 import datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PhysicalEntity(_message.Message):
    __slots__ = ("name", "type", "status", "parent_reference_frame", "state", "acceleration", "rotational_acceleration", "center_of_mass", "body_wrt_structural")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PARENT_REFERENCE_FRAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_MASS_FIELD_NUMBER: _ClassVar[int]
    BODY_WRT_STRUCTURAL_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    status: str
    parent_reference_frame: str
    state: _datatypes_pb2.SpaceTimeCoordinateState
    acceleration: _datatypes_pb2.AccelerationVector
    rotational_acceleration: _datatypes_pb2.AngularAccelerationVector
    center_of_mass: _datatypes_pb2.PositionVector
    body_wrt_structural: _datatypes_pb2.AttitudeQuaternion
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., status: _Optional[str] = ..., parent_reference_frame: _Optional[str] = ..., state: _Optional[_Union[_datatypes_pb2.SpaceTimeCoordinateState, _Mapping]] = ..., acceleration: _Optional[_Union[_datatypes_pb2.AccelerationVector, _Mapping]] = ..., rotational_acceleration: _Optional[_Union[_datatypes_pb2.AngularAccelerationVector, _Mapping]] = ..., center_of_mass: _Optional[_Union[_datatypes_pb2.PositionVector, _Mapping]] = ..., body_wrt_structural: _Optional[_Union[_datatypes_pb2.AttitudeQuaternion, _Mapping]] = ...) -> None: ...

class DynamicalEntity(_message.Message):
    __slots__ = ("name", "type", "status", "parent_reference_frame", "state", "acceleration", "rotational_acceleration", "center_of_mass", "body_wrt_structural", "force", "torque", "mass", "mass_rate", "inertia", "inertia_rate")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PARENT_REFERENCE_FRAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    ROTATIONAL_ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    CENTER_OF_MASS_FIELD_NUMBER: _ClassVar[int]
    BODY_WRT_STRUCTURAL_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    TORQUE_FIELD_NUMBER: _ClassVar[int]
    MASS_FIELD_NUMBER: _ClassVar[int]
    MASS_RATE_FIELD_NUMBER: _ClassVar[int]
    INERTIA_FIELD_NUMBER: _ClassVar[int]
    INERTIA_RATE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    status: str
    parent_reference_frame: str
    state: _datatypes_pb2.SpaceTimeCoordinateState
    acceleration: _datatypes_pb2.AccelerationVector
    rotational_acceleration: _datatypes_pb2.AngularAccelerationVector
    center_of_mass: _datatypes_pb2.PositionVector
    body_wrt_structural: _datatypes_pb2.AttitudeQuaternion
    force: _datatypes_pb2.ForceVector
    torque: _datatypes_pb2.TorqueVector
    mass: float
    mass_rate: float
    inertia: _containers.RepeatedScalarFieldContainer[float]
    inertia_rate: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., status: _Optional[str] = ..., parent_reference_frame: _Optional[str] = ..., state: _Optional[_Union[_datatypes_pb2.SpaceTimeCoordinateState, _Mapping]] = ..., acceleration: _Optional[_Union[_datatypes_pb2.AccelerationVector, _Mapping]] = ..., rotational_acceleration: _Optional[_Union[_datatypes_pb2.AngularAccelerationVector, _Mapping]] = ..., center_of_mass: _Optional[_Union[_datatypes_pb2.PositionVector, _Mapping]] = ..., body_wrt_structural: _Optional[_Union[_datatypes_pb2.AttitudeQuaternion, _Mapping]] = ..., force: _Optional[_Union[_datatypes_pb2.ForceVector, _Mapping]] = ..., torque: _Optional[_Union[_datatypes_pb2.TorqueVector, _Mapping]] = ..., mass: _Optional[float] = ..., mass_rate: _Optional[float] = ..., inertia: _Optional[_Iterable[float]] = ..., inertia_rate: _Optional[_Iterable[float]] = ...) -> None: ...

class PhysicalInterface(_message.Message):
    __slots__ = ("name", "parent_name", "position", "attitude")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_NAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ATTITUDE_FIELD_NUMBER: _ClassVar[int]
    name: str
    parent_name: str
    position: _datatypes_pb2.PositionVector
    attitude: _datatypes_pb2.AttitudeQuaternion
    def __init__(self, name: _Optional[str] = ..., parent_name: _Optional[str] = ..., position: _Optional[_Union[_datatypes_pb2.PositionVector, _Mapping]] = ..., attitude: _Optional[_Union[_datatypes_pb2.AttitudeQuaternion, _Mapping]] = ...) -> None: ...
