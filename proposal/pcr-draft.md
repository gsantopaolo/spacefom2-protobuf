# SISO Problem/Change Request (PCR): draft

Form layout and field instructions from SISO-ADM-003, *SISO Balloted Products Development and Support Process*, Appendix A. Fields the form says the submitter leaves blank are marked "(PSG)".

> The copy of the form consulted is SISO-ADM-003-2011. Ask the SpaceFOM PSG whether a newer PCR form is in use before submitting.

## Contents

- [Block 1](#block-1)
- [Block 2. General information](#block-2-general-information)
- [Block 3. Technical information](#block-3-technical-information)
  - [a. Problem/change request description](#a-problemchange-request-description)
  - [b. Analysis of the change](#b-analysis-of-the-change)
  - [c. Recommended action](#c-recommended-action)
- [Block 4. Impact analysis](#block-4-impact-analysis)
- [Block 5. Impacts on other standards or products](#block-5-impacts-on-other-standards-or-products)
- [Block 6. PCR action history](#block-6-pcr-action-history)
- [Block 7. Continuation](#block-7-continuation)
- [Block 8. Approved changes to documentation](#block-8-approved-changes-to-documentation)

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
| Phone 2 (DSN/Cell) | _to fill_ |
| Affiliation | Alloy Therapeutics, Inc.; contribution made in personal time |
| Submitter willing to be lead analyst | Yes |
| Present lead analyst | Gian Paolo Santopaolo |
| Lead analyst email | gianpaolo.santopaolo@gmail.com |
| Associated analysts | None |
| Source | Spec: X · Other: X (interoperability with non-HLA tools) |
| Type request | Change To Product: X |

**Document references**

| Document name | Doc No. | Paragraph |
|---|---|---|
| Space Reference Federation Object Model (SpaceFOM) | SISO-STD-018-2020 | §8.7 Data Types; Appendix C.2 to C.5 |
| HLA Federate Interface Specification (Federate Protocol) | IEEE 1516.1-2025 | _to fill: the clause number is not checked, because only the public 2024 draft `datatypes.proto` was read ([verification](../docs/verification.md#not-yet-verified))_ |

**Additional points of contact:** Alfredo Garro (University of Calabria), Vice Chair, SpaceFOM PDG.

## Block 3. Technical information

### a. Problem/change request description

This is a change request (a new capability). SpaceFOM datatypes are defined only as HLA OMT datatypes in the FOM modules and are exchanged only in HLA encoding. Systems outside an HLA federation (cloud data pipelines, Kafka, ROS 2, MBSE and data-analysis tools) have no standard, machine-readable schema for SpaceFOM data and must hand-write HLA decoders per type.

HLA 4 already uses Protocol Buffers to define the Federate Protocol services layer between federate and RTI. The change requested is that SpaceFOM 2.0 also provide a Protocol Buffers (`.proto`) description of the SpaceFOM datatypes and object classes, generated from the FOM XML, as an informative companion to the FOM modules. HLA remains the normative exchange mechanism inside the federation.

### b. Analysis of the change

- SpaceFOM 1.0 uses four basic representations: `HLAunicodeString`, `HLAinteger64Time`, `HLAinteger16LE`, `HLAfloat64LE` (§8.7.2.1), plus `HLAfixedArray` and `HLAfixedRecord` aggregates. No variant records are defined (§8.7.2.6). Each has a direct Protobuf equivalent (see the [mapping](../docs/technical-overview.md#mapping)).
- The FOM XML carries `<units>` on simple types and `<semantics>` on types and fields, and the generator copies them into the `.proto` as comments. The `<semantics>` text of the simple datatypes is not copied yet.
- A schema generated from the FOM stays consistent with each FOM revision. The generator is proven on the SpaceFOM 1.0 modules. SpaceFOM 2.0 changes, such as configurable time resolution, the updated epoch and the HLA 4 `Reference` datatype, need new generator rules, to be added as the 2.0 FOM drafts appear ([what 2.0 needs](../docs/technical-overview.md#what-spacefom-20-needs-from-the-generator)).
- An open-source prototype validates the mapping on the SpaceFOM 1.0 modules: the generator and the generated schema are built and tested in CI, with generated code tested in six languages. The bridge federate is planned.

### c. Recommended action

1. Add an informative annex, "Protocol Buffers representation of SpaceFOM datatypes", containing the mapping rules from HLA OMT datatypes to Protobuf.
2. Publish the generated `.proto` files with each SpaceFOM 2.0 release, next to the FOM modules.
3. Optionally, reference an open-source generator and bridge federate as a non-normative implementation.

Exact wording changes for Block 8 will be drafted once the PDG agrees on scope.

## Block 4. Impact analysis

_Initial view (to be completed in analysis):_ additive only. No change to existing object classes, interaction classes, datatypes, encodings, execution control or compliance rules; existing federates are unaffected.

## Block 5. Impacts on other standards or products

_Initial view:_ consistent with IEEE 1516-2025 (HLA 4), which already uses Protobuf for the Federate Protocol. To be completed in analysis.

## Block 6. PCR action history

(PSG)

## Block 7. Continuation

See the [technical overview](../docs/technical-overview.md) for the full mapping, an example generated `.proto`, and the bridge architecture.

## Block 8. Approved changes to documentation

(PSG; final approved changes only)
