# SISO Problem/Change Request (PCR) — draft

Form layout and field instructions from SISO-ADM-003, *SISO Balloted Products Development and Support Process*, Appendix A. Fields the form says the submitter leaves blank are marked "(PSG)".

> **Status of this template:** the copy consulted is SISO-ADM-003-2011. Ask the SpaceFOM PSG whether a newer PCR form is in use before submitting.

## Block 1

| Field | Value |
|---|---|
| PCR Title | Protobuf schema for the SpaceFOM datatypes, generated from the FOM modules |
| PCR No. | (PSG) |
| Category / Cat Name | Proposed: Datatypes / data exchange |
| Priority | (PSG) |
| Status | Open-FA |

## Block 2. General information

| Field | Value |
|---|---|
| Submitter | Gian Paolo Santopaolo |
| Date | _to fill on submission_ |
| Phone | _to fill_ |
| Email | gianpaolo.santopaolo@gmail.com |
| Affiliation | Alloy Therapeutics, Inc.; contribution made in personal time |
| Submitter willing to be lead analyst | Yes |
| Associated analysts | — |
| Source | Spec: X · Other: X (interoperability with non-HLA tools) |
| Type request | Change To Product: X |

**Document references**

| Document name | Doc No. | Paragraph |
|---|---|---|
| Space Reference Federation Object Model (SpaceFOM) | SISO-STD-018-2020 | §8.7 Data Types; Appendix C.2–C.5 |
| HLA Federate Interface Specification (Federate Protocol) | IEEE 1516.1-2025 | Federate Protocol clause |

**Additional points of contact:** Alfredo Garro (University of Calabria), Vice Chair, SpaceFOM PDG.

## Block 3. Technical information

### a. Problem/change request description

This is a change request (a new capability). SpaceFOM datatypes are defined only as HLA OMT datatypes in the FOM modules and are exchanged only in HLA encoding. Systems outside an HLA federation (cloud data pipelines, Kafka, ROS 2, MBSE and data-analysis tools) have no standard, machine-readable schema for SpaceFOM data and must hand-write HLA decoders per type.

HLA 4 already uses Protocol Buffers to define the Federate Protocol services layer between federate and RTI. The change requested is that SpaceFOM 2.0 also provide a Protocol Buffers (`.proto`) description of the SpaceFOM datatypes and object classes, generated from the FOM XML, as an informative companion to the FOM modules. HLA remains the normative exchange mechanism inside the federation.

### b. Analysis of the change

- SpaceFOM 1.0 uses four basic representations: `HLAunicodeString`, `HLAinteger64Time`, `HLAinteger16LE`, `HLAfloat64LE` (§8.7.2.1), plus `HLAfixedArray` and `HLAfixedRecord` aggregates. No variant records are defined (§8.7.2.6). Each has a direct Protobuf equivalent (see the [mapping](../docs/technical-overview.md#mapping)).
- The FOM XML carries `<units>` on simple types and `<semantics>` on types and fields, so units and meaning can be carried into the `.proto` as comments without loss.
- Generating the schema from the FOM, rather than hand-writing it, keeps it consistent with every FOM revision, including SpaceFOM 2.0 changes such as configurable time resolution, the updated epoch and the HLA 4 `Reference` datatype.
- A prototype generator and bridge federate are being developed in the open to validate the mapping on the SpaceFOM 1.0 modules.

### c. Recommended action

1. Add an informative annex, "Protocol Buffers representation of SpaceFOM datatypes", containing the mapping rules from HLA OMT datatypes to Protobuf.
2. Publish the generated `.proto` files with each SpaceFOM 2.0 release, next to the FOM modules.
3. Optionally, reference an open-source generator and bridge federate as a non-normative implementation.

Exact wording changes for Block 8 will be drafted once the PDG agrees on scope.

## Block 4. Impact analysis

_Initial view (to be completed in analysis):_ additive only. No change to existing object classes, interaction classes, datatypes, encodings, execution control or compliance rules; existing federates are unaffected.

## Block 5. Impacts on other standards or products

_Initial view:_ aligned with IEEE 1516-2025 (HLA 4), which already uses Protobuf for the Federate Protocol. No conflict identified with the SMP or FMI interoperability work. To be completed in analysis.

## Block 6. PCR action history

(PSG)

## Block 7. Continuation

See the [technical overview](../docs/technical-overview.md) for the full mapping, an example generated `.proto`, and the bridge architecture.

## Block 8. Approved changes to documentation

(PSG; final approved changes only)
