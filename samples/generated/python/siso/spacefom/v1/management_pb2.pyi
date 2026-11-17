# Derived from the SISO-STD-018-2020 (SpaceFOM) FOM modules.
# Reprinted with permission from SISO Inc.
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecutionMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EXEC_MODE_UNINITIALIZED: _ClassVar[ExecutionMode]
    EXEC_MODE_INITIALIZING: _ClassVar[ExecutionMode]
    EXEC_MODE_RUNNING: _ClassVar[ExecutionMode]
    EXEC_MODE_FREEZE: _ClassVar[ExecutionMode]
    EXEC_MODE_SHUTDOWN: _ClassVar[ExecutionMode]

class MTRMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MTR_MODE_UNSPECIFIED: _ClassVar[MTRMode]
    MTR_GOTO_RUN: _ClassVar[MTRMode]
    MTR_GOTO_FREEZE: _ClassVar[MTRMode]
    MTR_GOTO_SHUTDOWN: _ClassVar[MTRMode]
EXEC_MODE_UNINITIALIZED: ExecutionMode
EXEC_MODE_INITIALIZING: ExecutionMode
EXEC_MODE_RUNNING: ExecutionMode
EXEC_MODE_FREEZE: ExecutionMode
EXEC_MODE_SHUTDOWN: ExecutionMode
MTR_MODE_UNSPECIFIED: MTRMode
MTR_GOTO_RUN: MTRMode
MTR_GOTO_FREEZE: MTRMode
MTR_GOTO_SHUTDOWN: MTRMode

class ExecutionConfiguration(_message.Message):
    __slots__ = ("root_frame_name", "scenario_time_epoch", "current_execution_mode", "next_execution_mode", "next_mode_scenario_time", "next_mode_cte_time", "least_common_time_step")
    ROOT_FRAME_NAME_FIELD_NUMBER: _ClassVar[int]
    SCENARIO_TIME_EPOCH_FIELD_NUMBER: _ClassVar[int]
    CURRENT_EXECUTION_MODE_FIELD_NUMBER: _ClassVar[int]
    NEXT_EXECUTION_MODE_FIELD_NUMBER: _ClassVar[int]
    NEXT_MODE_SCENARIO_TIME_FIELD_NUMBER: _ClassVar[int]
    NEXT_MODE_CTE_TIME_FIELD_NUMBER: _ClassVar[int]
    LEAST_COMMON_TIME_STEP_FIELD_NUMBER: _ClassVar[int]
    root_frame_name: str
    scenario_time_epoch: float
    current_execution_mode: ExecutionMode
    next_execution_mode: ExecutionMode
    next_mode_scenario_time: float
    next_mode_cte_time: float
    least_common_time_step: int
    def __init__(self, root_frame_name: _Optional[str] = ..., scenario_time_epoch: _Optional[float] = ..., current_execution_mode: _Optional[_Union[ExecutionMode, str]] = ..., next_execution_mode: _Optional[_Union[ExecutionMode, str]] = ..., next_mode_scenario_time: _Optional[float] = ..., next_mode_cte_time: _Optional[float] = ..., least_common_time_step: _Optional[int] = ...) -> None: ...

class ModeTransitionRequest(_message.Message):
    __slots__ = ("execution_mode",)
    EXECUTION_MODE_FIELD_NUMBER: _ClassVar[int]
    execution_mode: MTRMode
    def __init__(self, execution_mode: _Optional[_Union[MTRMode, str]] = ...) -> None: ...
