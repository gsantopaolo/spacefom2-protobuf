<div align="center">

# SpaceFOM ⇄ Protobuf

**A Protocol Buffers schema for the SISO SpaceFOM datatypes, generated from the FOM modules —<br>a bridge that lets cloud, streaming, robotics and MBSE tools read space-simulation data without speaking HLA.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-proposal-orange.svg)
![Target](https://img.shields.io/badge/target-SpaceFOM%202.0-6f42c1.svg)
![Base](https://img.shields.io/badge/based%20on-SISO--STD--018--2020-555.svg)

<img src="docs/images/bridge-architecture.svg" alt="HLA stays inside the federation; Protobuf carries SpaceFOM data out" width="760">

</div>

## What this is

[SpaceFOM](https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf) (SISO-STD-018-2020) is the SISO standard for interoperable, HLA-based space-mission simulation, now being evolved into **SpaceFOM 2.0** by the SISO Product Development Group.

Today, SpaceFOM data can only be read by software that speaks HLA. This project proposes that SpaceFOM 2.0 also publish a **`.proto` schema of its datatypes, generated mechanically from the FOM XML**, plus a reference **bridge federate** that republishes HLA updates as Protobuf on Kafka or gRPC.

HLA is not replaced: federation roles, synchronization and time management stay in HLA. The schema simply opens SpaceFOM data to everything outside the federation.

## Read the proposal

| Document | What it is |
|---|---|
| **[One-page pitch](proposal/pitch.md)** | Problem, solution, expected benefits, proposer: the summary for the SpaceFOM 2.0 PDG |
| [Draft PCR](proposal/pcr-draft.md) | The proposal on the SISO Problem/Change Request form (SISO-ADM-003, Appendix A) |
| [Technical overview](docs/technical-overview.md) | HLA-to-Protobuf mapping, example `.proto`, architecture, open questions |
| [Verification](docs/verification.md) | Every technical claim, with the clause of the standard it was checked against |
| [Generator and CI plan](docs/plans/generator-ci-plan.md) | Draft plan for the FOM XML → `.proto` generator and the GitHub Action that opens update PRs |

## Example

`ReferenceFrame`, as defined in SISO-STD-018-2020 (Tables C-4 to C-7, C-13), rendered as Protobuf. Full file: [docs/examples/reference_frame.proto](docs/examples/reference_frame.proto).

```protobuf
message SpaceTimeCoordinateState {
  ReferenceFrameTranslation translational_state = 1;
  ReferenceFrameRotation rotational_state = 2;
  double time = 3;  // Time: simulated physical time (TT), s
}

message ReferenceFrame {
  optional string name = 1;
  optional string parent_name = 2;  // empty for the root frame
  optional SpaceTimeCoordinateState state = 3;
}
```

## Roadmap

- [x] Proposal, draft PCR and verified example schema
- [ ] FOM XML → `.proto` generator, with CI
- [ ] Bridge federate: HLA updates → Protobuf → Kafka / gRPC
- [ ] Docker Compose demo: sample federation, bridge and non-HLA consumers
- [ ] Technical documentation and diagrams for the PDG hearing

## Repository layout

```
proposal/   one-page pitch and draft PCR
docs/       technical overview, verification, diagrams, example .proto
```

## Disclaimer

Independent proposal by [Gian Paolo Santopaolo](https://github.com/gsantopaolo). Not affiliated with, endorsed by, or an official product of SISO, NASA or any other organization. SpaceFOM and SISO-STD-018-2020 are © SISO; this repository does not reproduce the standard and refers to it by clause. The `.proto` definitions are derived from the SpaceFOM FOM modules: Reprinted with permission from SISO Inc.

Prepared with Claude (Anthropic) as a research and drafting aid; every technical fact was checked against the primary sources listed in [verification](docs/verification.md).

## License

[MIT](LICENSE) © 2026 Gian Paolo Santopaolo
