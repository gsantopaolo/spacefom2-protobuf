# SpaceFOM 2.0 Proposal: Protobuf Schema for SpaceFOM Datatypes

Gianpaolo Santopaolo · 17 November 2026

## Summary

SpaceFOM 2.0 should publish, alongside its FOM modules, a Protocol Buffers (`.proto`) schema of the SpaceFOM datatypes, generated mechanically from the FOM XML. It does not replace HLA: federation roles, synchronization and time management stay in HLA. It gives tools outside the HLA world (cloud pipelines, Kafka, ROS 2, MBSE and data-analysis tools) a standard, typed way to read and write SpaceFOM data.

## Problem

Today, SpaceFOM data can only be read by software that speaks HLA. The datatypes (reference frames, space-time coordinate states, physical and dynamical entities) are defined in the `SISO_SpaceFOM_datatypes`, `_environment` and `_entity` FOM modules and travel in HLA encoding: little-endian `HLAfloat64LE` values inside `HLAfixedRecord`s and `HLAfixedArray`s, with HLA logical time as big-endian `HLAinteger64Time` [1, §8.7.3].

- **HLA 4 already uses Protobuf, but for the services, not the data.** The new Federate Protocol defines the HLA services layer between federate and RTI using Protobuf [5, §2.1]. The data itself keeps the HLA encodings; HLA 4 even adds a new one, `HLAextendableVariantRecord` [5].
- **Consumers outside the federation must re-implement HLA decoding.** A cloud pipeline, a Kafka stream, a ROS 2 node or an MBSE/data-analysis tool that only wants to read a vehicle's state has to hand-write decoders for each SpaceFOM type, with no shared, versioned schema.
- **The result:** SpaceFOM simulation data stays locked inside HLA federations, which works against the goal of opening SpaceFOM to MBSE, data analysis and other industrial standards.

## Proposed solution

**Hypothesis:** the SpaceFOM datatypes map cleanly onto Protobuf, so a `.proto` schema can be generated from the FOM modules and kept in sync with them automatically. SpaceFOM 1.0 uses only four basic representations (`HLAunicodeString`, `HLAinteger64Time`, `HLAinteger16LE`, `HLAfloat64LE`) and no variant records [1, §8.7.2], so the mapping is small.

1. **A deterministic FOM-to-proto mapping**, published as an annex of SpaceFOM 2.0:
    - Basic representations → Protobuf scalars: `HLAfloat64LE` → `double`, `HLAinteger64Time` → `int64`, `HLAunicodeString` → `string`.
    - Enumerations (`ExecutionMode`, `MTRMode`, `HLAinteger16LE`) → `enum`s; fixed records → `message`s; 3-element fixed arrays → vector messages, 9-element arrays (inertia matrices) → `repeated double`. If SpaceFOM 2.0 adds variant records, they map to `oneof`.
    - Object classes → one `message` per class, with all attributes optional, so a partial attribute update maps to a partial message.
    - The FOM XML already carries `<units>` on every simple type and `<semantics>` on every type and field; the generator copies them into the `.proto` as comments, so units are never lost.
2. **A reference generator** that reads the FOM XML and writes the `.proto` files, run in CI so the schema can never drift from the FOM.
3. **A reference bridge federate** that subscribes via HLA (or the HLA 4 Federate Protocol), converts HLA-encoded values to Protobuf, and publishes them to Kafka or gRPC.

![Where the Protobuf bridge sits](bridge-architecture.svg)

The federation is untouched; the bridge and the generated schema are the only new parts.

Example output for `ReferenceFrame` (types and field names as defined in SISO-STD-018-2020, Tables C-4 to C-7 and C-13, and in `SISO_SpaceFOM_datatypes.xml`):

```protobuf
syntax = "proto3";
package siso.spacefom.v1;

// PositionVector, VelocityVector, AngularVelocityVector, Vector:
// HLAfixedArray of 3 x HLAfloat64LE
message PositionVector        { double x = 1; double y = 2; double z = 3; }  // m
message VelocityVector        { double x = 1; double y = 2; double z = 3; }  // m/s
message AngularVelocityVector { double x = 1; double y = 2; double z = 3; }  // rad/s
message Vector                { double x = 1; double y = 2; double z = 3; }  // unitless

// Left unit transformation quaternion, Q = (s, V)
message AttitudeQuaternion {
  double scalar = 1;
  Vector vector = 2;
}

message ReferenceFrameTranslation {
  PositionVector position = 1;
  VelocityVector velocity = 2;
}

message ReferenceFrameRotation {
  AttitudeQuaternion attitude_quaternion = 1;
  AngularVelocityVector angular_velocity = 2;
}

message SpaceTimeCoordinateState {
  ReferenceFrameTranslation translational_state = 1;
  ReferenceFrameRotation rotational_state = 2;
  double time = 3;  // Time: simulated physical time (TT), s
}

// Object class HLAobjectRoot.ReferenceFrame
message ReferenceFrame {
  optional string name = 1;
  optional string parent_name = 2;  // empty for the root frame
  optional SpaceTimeCoordinateState state = 3;
}
```

**Out of scope:** replacing HLA, its RTI services, roles, synchronization or time management. The `.proto` describes the data only; HLA remains the source of truth inside the federation.

## Expected benefits

- **SpaceFOM data reaches beyond HLA.** Any language with a Protobuf code generator gets typed SpaceFOM classes for free. This directly serves the strategic goal of opening SpaceFOM to MBSE, data analysis and other standards, next to the existing SMP and FMI bridges.
- **One schema, no hand-written decoders.** Generated from the FOM and checked in CI, the `.proto` is always in step with the standard and versioned with it.
- **Consistent with HLA 4.** It uses the same technology the Federate Protocol already adopted for its services layer, so HLA 4 tool vendors and federate developers find nothing new to learn.
- **Built for streaming and storage.** Compact binary encoding, schema evolution rules and native Kafka/gRPC support make recording, replay and cloud analysis of federation runs straightforward.
- **Low cost and low risk.** It is additive: no change to existing federates, the RTI or compliance rules. It can start as an informative annex and become normative later if the group wishes.

## Proposed next steps

1. **Hearing:** present the idea to the PDG with a few slides and a working demo.
2. **Prototype:** a generator that produces `.proto` files from the published SpaceFOM 1.0 modules, plus a bridge federate streaming `ReferenceFrame` and `PhysicalEntity` updates from a sample federation to Kafka.
3. **Specification:** if the group agrees, draft the FOM-to-proto mapping rules as an annex for SpaceFOM 2.0 and track it as a change request (PCR).

Open question for the group: should the mapping also cover interaction classes and the management module, or start with the environment and entity data only?

## Proposer

**Gianpaolo Santopaolo** is a Senior AI/ML Engineer at Alloy Therapeutics in Lugano, Switzerland, a position he reached through experience rather than a formal engineering degree. _[Role: one line on what you do at Alloy — to confirm.]_

He has more than 20 years of experience architecting and implementing highly available, highly scalable, distributed real-time systems deployed worldwide, and has used Protocol Buffers in production for years, speaking publicly on the subject. He was a Microsoft Regional Director for 2 years and a Microsoft MVP for 10 years.

### How this proposal was prepared

The idea is mine and comes from years of working with Protocol Buffers: noticing that HLA 4 adopted Protobuf for its services layer, I asked whether SpaceFOM data could use it too. I used Claude (Anthropic's AI assistant) as a research and writing aid throughout. It located and read the SpaceFOM papers and the HLA 4 technical summary, transcribed and summarized my discussion with the PDG, and drafted this text from my notes and our work together. Every datatype, field name and encoding in this document was then checked against the primary sources: SISO-STD-018-2020 and the SpaceFOM FOM XML modules. I reviewed the result, and I stand behind it.

## References

1. [SISO-STD-018-2020, Space Reference FOM (SpaceFOM) 1.0](https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf): §8.7 and Appendix C
2. [SpaceFOM 1.0 FOM modules (XML)](https://github.com/nasa/TrickHLA/tree/master/FOMs/SpaceFOM), as distributed in NASA TrickHLA
3. Crues, Dexter, Falcone, Garro, Möller, ["SpaceFOM – A robust standard for enabling a-priori interoperability of HLA-based space systems simulations"](https://doi.org/10.1080/17477778.2021.1945962), Journal of Simulation 16(6), 2022
4. ["SpaceFOM V2: The Next Generation in Space Simulation Interoperability and How You Can Help"](https://ntrs.nasa.gov/citations/20260008222), SISO SIMposium, Sept 2026
5. Möller, Karlsson et al., ["A Summary of Technical Updates in HLA 4 (IEEE 1516-2025)"](https://onearc.com/wp-content/uploads/2026/02/SISO_2026_SIW_028.pdf), SISO SIW 2026, paper 028
6. ["SpaceFOM: An Interoperability Standard for Space Systems Simulations"](https://ntrs.nasa.gov/api/citations/20210021609/downloads/SpaceFOM_IEEE_2022_Aeroconf.docx.pdf), IEEE Aerospace Conference 2022
