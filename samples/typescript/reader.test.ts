// Tests for the generated TypeScript bindings (run: npm test, from samples/).
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  create,
  equals,
  fromBinary,
  toBinary,
  ScalarType,
  type DescField,
  type DescFile,
  type DescMessage,
} from "@bufbuild/protobuf";
import { reflect, type ReflectMessage } from "@bufbuild/protobuf/reflect";
import { file_siso_spacefom_v1_datatypes } from "../generated/typescript/siso/spacefom/v1/datatypes_pb.js";
import { file_siso_spacefom_v1_entity } from "../generated/typescript/siso/spacefom/v1/entity_pb.js";
import { file_siso_spacefom_v1_environment, ReferenceFrameSchema } from "../generated/typescript/siso/spacefom/v1/environment_pb.js";
import {
  ExecutionModeSchema,
  file_siso_spacefom_v1_management,
  MTRMode,
  MTRModeSchema,
} from "../generated/typescript/siso/spacefom/v1/management_pb.js";
import { verify } from "./reader.ts";

const EXPECTED_MESSAGES = 18;
const files: DescFile[] = [
  file_siso_spacefom_v1_datatypes,
  file_siso_spacefom_v1_environment,
  file_siso_spacefom_v1_entity,
  file_siso_spacefom_v1_management,
];
const allMessages: DescMessage[] = files.flatMap((f) => f.messages);

function scalar(field: DescField): unknown {
  if (field.fieldKind === "enum") return field.enum.values[field.enum.values.length - 1].number;
  if (field.fieldKind === "scalar" || field.fieldKind === "list") {
    switch (field.scalar) {
      case ScalarType.DOUBLE: return 1.25;
      case ScalarType.INT64: return 7n;
      case ScalarType.STRING: return "x";
    }
  }
  throw new Error(`unexpected field ${field.toString()}`);
}

// Set every field (recursively) to a non-default value.
function fill(message: ReflectMessage): void {
  for (const field of message.fields) {
    if (field.fieldKind === "message") {
      const child = reflect(field.message);
      fill(child);
      message.set(field, child);
    } else if (field.fieldKind === "list") {
      const list = message.get(field);
      for (let i = 0; i < 9; i++) list.add(scalar(field));
    } else {
      message.set(field, scalar(field));
    }
  }
}

test("fixture values", () => {
  assert.equal(verify(), 5);
});

test("every message type is generated", () => {
  assert.equal(allMessages.length, EXPECTED_MESSAGES);
});

for (const desc of allMessages) {
  test(`${desc.name} round-trips with all fields set`, () => {
    const original = reflect(desc);
    fill(original);
    assert.equal(original.fields.filter((f) => original.isSet(f)).length, desc.fields.length);
    const decoded = fromBinary(desc, toBinary(desc, original.message));
    assert.ok(equals(desc, decoded, original.message));
  });
}

test("enums", () => {
  assert.deepEqual(ExecutionModeSchema.values.map((v) => v.number), [0, 1, 2, 3, 4]);
  assert.equal(MTRMode.MTR_MODE_UNSPECIFIED, 0);
  assert.deepEqual(MTRModeSchema.values.map((v) => v.number), [0, 2, 3, 4]);
});

test("optional presence", () => {
  const frame = create(ReferenceFrameSchema, { parentName: "" });
  const decoded = fromBinary(ReferenceFrameSchema, toBinary(ReferenceFrameSchema, frame));
  assert.equal(decoded.parentName, "");
  assert.equal(create(ReferenceFrameSchema).parentName, undefined);
});
