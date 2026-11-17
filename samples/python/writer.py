"""Write the shared sample data that every reader in samples/ decodes.

Each message goes to its own file in samples/data/, as protobuf binary
(.binpb) plus protobuf JSON (.json) for reading by eye.
"""

import sys
from pathlib import Path

SAMPLES = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SAMPLES / "generated" / "python"))

from google.protobuf import json_format  # noqa: E402

from siso.spacefom.v1 import entity_pb2, environment_pb2, management_pb2  # noqa: E402


def build() -> dict:
    root = environment_pb2.ReferenceFrame(name="RootFrame", parent_name="")
    root.state.time = 0.0

    child = environment_pb2.ReferenceFrame(name="EarthFrame", parent_name="RootFrame")
    child.state.translational_state.position.x = 1.4959787e11
    child.state.translational_state.velocity.y = 29780.0
    child.state.rotational_state.attitude_quaternion.scalar = 1.0
    child.state.rotational_state.angular_velocity.z = 7.2921159e-5
    child.state.time = 1.5

    entity = entity_pb2.DynamicalEntity(
        name="Lander1",
        type="Lander",
        status="Active",
        parent_reference_frame="EarthFrame",
        mass=15000.0,
        mass_rate=-1.25,
        inertia=[1000.0, 0.0, 0.0, 0.0, 2000.0, 0.0, 0.0, 0.0, 3000.0],
    )
    entity.state.translational_state.position.x = 6778137.0
    entity.state.translational_state.velocity.y = 7668.6
    entity.state.rotational_state.attitude_quaternion.scalar = 1.0
    entity.state.time = 1.5
    entity.force.x = 100.5
    entity.center_of_mass.z = 0.3
    # torque is deliberately left unset: readers check that it is absent.

    config = management_pb2.ExecutionConfiguration(
        root_frame_name="RootFrame",
        current_execution_mode=management_pb2.EXEC_MODE_RUNNING,
        next_execution_mode=management_pb2.EXEC_MODE_FREEZE,
        next_mode_scenario_time=100.0,
        least_common_time_step=250000,
    )

    mtr = management_pb2.ModeTransitionRequest(execution_mode=management_pb2.MTR_GOTO_FREEZE)

    return {
        "reference_frame_root": root,
        "reference_frame_child": child,
        "dynamical_entity": entity,
        "execution_configuration": config,
        "mode_transition_request": mtr,
    }


def main() -> None:
    out = SAMPLES / "data"
    out.mkdir(exist_ok=True)
    for name, message in build().items():
        (out / f"{name}.binpb").write_bytes(message.SerializeToString(deterministic=True))
        text = json_format.MessageToJson(message, preserving_proto_field_name=True, indent=2)
        (out / f"{name}.json").write_text(text + "\n", encoding="utf-8")
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
