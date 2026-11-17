// Decode the shared sample data and check every value (see samples/README.md).
import { readFileSync } from "node:fs";
import { fromBinary, toBinary, equals, type DescMessage, type MessageShape } from "@bufbuild/protobuf";
import { ReferenceFrameSchema } from "../generated/typescript/siso/spacefom/v1/environment_pb.js";
import { DynamicalEntitySchema } from "../generated/typescript/siso/spacefom/v1/entity_pb.js";
import {
  ExecutionConfigurationSchema,
  ExecutionMode,
  MTRMode,
  ModeTransitionRequestSchema,
} from "../generated/typescript/siso/spacefom/v1/management_pb.js";

function load<D extends DescMessage>(schema: D, name: string): MessageShape<D> {
  const bytes = readFileSync(new URL(`../data/${name}.binpb`, import.meta.url));
  return fromBinary(schema, bytes);
}

function check(ok: boolean, what: string): void {
  if (!ok) throw new Error(what);
}

/** Check every value in the shared data; returns the number of messages checked. */
export function verify(): number {
  const root = load(ReferenceFrameSchema, "reference_frame_root");
  check(root.name === "RootFrame", "root frame name");
  check(root.parentName !== undefined && root.parentName === "", "root parent_name present and empty");

  const child = load(ReferenceFrameSchema, "reference_frame_child");
  check(child.parentName === "RootFrame", "child parent_name");
  check(child.state?.translationalState?.position?.x === 1.4959787e11, "child position.x");
  check(child.state?.rotationalState?.angularVelocity?.z === 7.2921159e-5, "child angular_velocity.z");

  const entity = load(DynamicalEntitySchema, "dynamical_entity");
  check(entity.name === "Lander1", "entity name");
  check(entity.mass === 15000.0, "entity mass");
  check(entity.inertia.length === 9 && entity.inertia[4] === 2000.0, "entity inertia");
  check(entity.state?.time === 1.5, "entity state.time");
  check(entity.force?.x === 100.5, "entity force");
  check(entity.torque === undefined, "entity torque absent");

  const config = load(ExecutionConfigurationSchema, "execution_configuration");
  check(config.currentExecutionMode === ExecutionMode.EXEC_MODE_RUNNING, "current_execution_mode");
  check(config.nextExecutionMode === ExecutionMode.EXEC_MODE_FREEZE, "next_execution_mode");
  check(config.leastCommonTimeStep === 250000n, "least_common_time_step");

  const mtr = load(ModeTransitionRequestSchema, "mode_transition_request");
  check(mtr.executionMode === MTRMode.MTR_GOTO_FREEZE, "MTR execution_mode");

  const again = fromBinary(DynamicalEntitySchema, toBinary(DynamicalEntitySchema, entity));
  check(equals(DynamicalEntitySchema, again, entity), "round trip");
  return 5;
}

if (import.meta.main) {
  try {
    console.log(`OK typescript: ${verify()} messages checked`);
  } catch (err) {
    console.error(`FAIL typescript: ${(err as Error).message}`);
    process.exit(1);
  }
}
