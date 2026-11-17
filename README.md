# SpaceFOM 2.0 – Protobuf schema for SpaceFOM datatypes

Proposal and proof of concept for generating a Protocol Buffers (`.proto`) schema of the
SISO SpaceFOM datatypes from the FOM modules, as a bridge (not a replacement) for HLA.

## Layout

| Path | Contents |
|---|---|
| `proposal/` | The proposal for the SpaceFOM 2.0 PDG and its architecture diagram |
| `proposal/examples/` | Example `.proto` output, verified against SISO-STD-018-2020 |

`reference-docs/` (standards, papers, private notes) is kept locally and excluded from git.

## Planned POC

1. FOM XML → `.proto` generator
2. Bridge federate: HLA updates → Protobuf → Kafka/gRPC
3. CI (GitHub Actions) regenerating and validating the schema
