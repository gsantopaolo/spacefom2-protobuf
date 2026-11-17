# SpaceFOM 2.0 – Protobuf schema for SpaceFOM datatypes

Proposal and proof of concept for generating a Protocol Buffers (`.proto`) schema of the
SISO SpaceFOM datatypes from the FOM modules, as a bridge (not a replacement) for HLA.

## Layout

| Path | Contents |
|---|---|
| `proposal/` | The proposal for the SpaceFOM 2.0 PDG and its architecture diagram |
| `reference-docs/` | Papers, the conversation handoff and the original voice message |
| `reference-docs/alfredo-message/transcribe.py` | Italian speech-to-text with mlx-whisper (Apple Silicon) |

## Planned POC

1. FOM XML → `.proto` generator
2. Bridge federate: HLA updates → Protobuf → Kafka/gRPC
3. CI (GitHub Actions) regenerating and validating the schema
