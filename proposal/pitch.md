# SpaceFOM 2.0: a Protobuf schema for the SpaceFOM datatypes

**Proposed by** Gian Paolo Santopaolo · 17 November 2026 · for the SISO SpaceFOM 2.0 PDG

## Problem

SpaceFOM data can only be consumed by software that speaks HLA. Reference frames, space-time coordinate states and entities travel as HLA-encoded records (`HLAfloat64LE` fields in `HLAfixedRecord`s, SISO-STD-018-2020 §8.7). A cloud pipeline, a Kafka stream, a ROS 2 node or an MBSE/data-analysis tool that just wants to read a vehicle's state must hand-write decoders for every type, with no shared, versioned schema. HLA 4 already defines its Federate Protocol services layer in Protobuf (SISO SIW 2026-028 §2.1), but the SpaceFOM data itself has no equivalent.

## Hypothesis and solution

The SpaceFOM datatypes map cleanly onto Protocol Buffers: SpaceFOM 1.0 uses only four basic representations and no variant records (§8.7.2). So SpaceFOM 2.0 can publish, **alongside its FOM modules, a `.proto` schema generated mechanically from the FOM XML**:

- a deterministic **FOM-to-proto mapping**, as an informative annex;
- a **reference generator**, run in CI, so the schema never drifts from the FOM (and follows 2.0 changes such as configurable time resolution);
- a **reference bridge federate** that republishes HLA updates as Protobuf on Kafka or gRPC.

HLA is not replaced: roles, synchronization and time management stay in HLA, which remains the source of truth inside the federation.

## Expected benefits

- **Opens SpaceFOM beyond HLA**, toward MBSE, data analysis, cloud and robotics, next to the existing SMP and FMI bridges.
- **One schema, typed code in any language**, with no hand-written decoders.
- **Consistent with HLA 4**, which already chose Protobuf for its services layer.
- **Ready for streaming, recording and replay** of federation runs.
- **Additive and low risk**: no change to federates, the RTI or compliance rules.

## Who proposes it

**Gian Paolo Santopaolo**, Senior AI/ML Engineer at Alloy Therapeutics (Basel, Switzerland), a position reached through experience rather than a formal engineering degree, where he leads the design and deployment of conversational and agentic AI systems that let scientists work with proprietary research data. More than 20 years architecting and implementing highly available, highly scalable, distributed real-time systems worldwide; long-time Protocol Buffers user and speaker; Microsoft Regional Director (2 years) and Microsoft MVP (10 years). Available to present the idea with a working demo and to act as lead analyst for the PCR.

<sub>Prepared with Claude (Anthropic) as a research and drafting aid; every technical fact was checked against SISO-STD-018-2020 and the SpaceFOM FOM XML. I reviewed it and stand behind it. Details: [technical overview](../docs/technical-overview.md) · [draft PCR](pcr-draft.md).</sub>
