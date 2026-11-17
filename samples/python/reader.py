"""Decode the shared sample data and check every value (see samples/README.md)."""

import sys
from pathlib import Path

SAMPLES = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SAMPLES / "generated" / "python"))

from siso.spacefom.v1 import entity_pb2, environment_pb2, management_pb2  # noqa: E402

DATA = SAMPLES / "data"


def load(message_type, name):
    message = message_type()
    message.ParseFromString((DATA / f"{name}.binpb").read_bytes())
    return message


def check(condition, what):
    if not condition:
        raise AssertionError(what)


def verify() -> int:
    """Check every value in the shared data. Returns the number of messages checked."""
    root = load(environment_pb2.ReferenceFrame, "reference_frame_root")
    check(root.name == "RootFrame", "root frame name")
    check(root.HasField("parent_name") and root.parent_name == "", "root parent_name present and empty")

    child = load(environment_pb2.ReferenceFrame, "reference_frame_child")
    check(child.parent_name == "RootFrame", "child parent_name")
    check(child.state.translational_state.position.x == 1.4959787e11, "child position.x")
    check(child.state.rotational_state.angular_velocity.z == 7.2921159e-5, "child angular_velocity.z")

    entity = load(entity_pb2.DynamicalEntity, "dynamical_entity")
    check(entity.name == "Lander1", "entity name")
    check(entity.mass == 15000.0, "entity mass")
    check(len(entity.inertia) == 9 and entity.inertia[4] == 2000.0, "entity inertia")
    check(entity.state.time == 1.5, "entity state.time")
    check(entity.HasField("force") and entity.force.x == 100.5, "entity force")
    check(not entity.HasField("torque"), "entity torque absent")

    config = load(management_pb2.ExecutionConfiguration, "execution_configuration")
    check(config.current_execution_mode == management_pb2.EXEC_MODE_RUNNING, "current_execution_mode")
    check(config.next_execution_mode == management_pb2.EXEC_MODE_FREEZE, "next_execution_mode")
    check(config.least_common_time_step == 250000, "least_common_time_step")

    mtr = load(management_pb2.ModeTransitionRequest, "mode_transition_request")
    check(mtr.execution_mode == management_pb2.MTR_GOTO_FREEZE, "MTR execution_mode")

    again = entity_pb2.DynamicalEntity()
    again.ParseFromString(entity.SerializeToString())
    check(again == entity, "round trip")
    return 5


def main() -> None:
    try:
        count = verify()
    except AssertionError as exc:
        sys.exit(f"FAIL python: {exc}")
    print(f"OK python: {count} messages checked")


if __name__ == "__main__":
    main()
