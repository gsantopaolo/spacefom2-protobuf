# Technical overview: SpaceFOM datatypes as Protocol Buffers

Companion to the [one-page pitch](../proposal/pitch.md) and the [draft PCR](../proposal/pcr-draft.md). Every datatype, field name and encoding below was checked against SISO-STD-018-2020 and the SpaceFOM 1.0 FOM XML; see [verification](verification.md).

## Contents

- [Where it fits](#where-it-fits)
- [Encoding today](#encoding-today)
- [Mapping](#mapping)
- [Example output](#example-output)
- [SpaceFOM 2.0 changes the generator must follow](#spacefom-20-changes-the-generator-must-follow)
- [Open questions for the PDG](#open-questions-for-the-pdg)
- [References](#references)

## Where it fits

![HLA stays inside the federation; Protobuf carries SpaceFOM data out](images/bridge-architecture.svg)

The federation is untouched. Two parts are new:

- **Generator:** reads the SpaceFOM FOM modules (IEEE 1516-2010 DIF XML) and writes `.proto` files. It runs in CI, so the schema is regenerated whenever the FOM changes.
- **Bridge federate:** joins the federation like any other federate (classic HLA API, or the HLA 4 Federate Protocol), reflects SpaceFOM object updates, converts them to the generated Protobuf messages and publishes them to Kafka or gRPC.

Out of scope: replacing HLA, its RTI services, federate roles, synchronization or time management.

## Encoding today

SpaceFOM uses Little Endian everywhere except HLA logical time (`HLAinteger64Time`, whose underlying representation `HLAinteger64BE` is Big Endian) (SISO-STD-018-2020 §8.7.3). Its datatypes are built on four basic representations (§8.7.2.1):

| Basic representation | Used for |
|---|---|
| `HLAfloat64LE` | All simple datatypes: `Length`, `Velocity`, `Time`, `Mass`, `Scalar`, … (Table 8-2) |
| `HLAinteger16LE` | Enumerations `ExecutionMode`, `MTRMode` (Tables C-10, C-11) |
| `HLAinteger64Time` | HLA logical time and lookahead |
| `HLAunicodeString` | Names and identifiers (e.g. `ReferenceFrame.name`, `PhysicalEntity.parent_reference_frame`) |

HLA 4's Federate Protocol does not change this. Its Protobuf messages carry each attribute or parameter value as an opaque `bytes` field (`AttributeHandleValue.value`, `ParameterHandleValue.value` in the IEEE 1516.1 Federate Protocol `datatypes.proto`, reprinted with permission from IEEE 1516.1(TM)-2024), so a consumer still needs the FOM and an HLA decoder to read the data.

Aggregates are `HLAfixedArray` (3-vectors and 3×3 matrices, Tables C-3) and `HLAfixedRecord` (Tables C-4 to C-7). SpaceFOM 1.0 defines no variant records (§8.7.2.6).

## Mapping

| HLA OMT construct | Protobuf | Notes |
|---|---|---|
| `HLAfloat64LE` simple datatype | `double` | Unit from the FOM `<units>` element, copied as a comment |
| `HLAinteger64Time` | `int64` | SpaceFOM 1.0: microseconds since the start of the federation execution (FOM `<time>` semantics); configurable resolution in 2.0 |
| `HLAinteger16LE` enumeration | `enum` | Enumerator names and values kept as in the FOM |
| `HLAunicodeString` | `string` | |
| `HLAfixedArray`, cardinality 3 | message with `x`, `y`, `z` | One message per named array type (`PositionVector`, `VelocityVector`, …), so types stay distinct |
| `HLAfixedArray`, cardinality 9 | `repeated double` (9 elements, row-wise) | `InertiaMatrix`, `Matrix`, `InertiaRateMatrix` |
| `HLAfixedRecord` | `message` | Field order preserved |
| Variant record (none in 1.0) | `oneof` | For SpaceFOM 2.0 / HLA 4 `HLAextendableVariantRecord` if adopted |
| Object class | `message`, all attributes `optional` | A partial attribute update maps to a partial message |
| Interaction class | `message` | Open question for the PDG whether to include |
| `<semantics>` | Comment on the message or field | Carried verbatim |

## Example output

`ReferenceFrame` and the types it depends on (Tables C-4 to C-7, C-13; `SISO_SpaceFOM_datatypes.xml`). The file is [examples/reference_frame.proto](examples/reference_frame.proto) and compiles with `protoc`.

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

## SpaceFOM 2.0 changes the generator must follow

From the SISO SIMposium 2026 presentation "SpaceFOM V2 … and How You Can Help":

- configurable time resolution (`BASE_TIME_SECONDS` … `BASE_TIME_ATTOSECONDS`) and an updated epoch (2000);
- HLA 4 directed interactions and the new `Reference` datatype;
- extended object classes drawn from NASA Artemis and ESA HRAF3 experience.

Because the schema is generated from the FOM, these become generator rules rather than hand edits.

## Open questions for the PDG

1. Scope: environment and entity modules only, or also management (`ExecutionConfiguration`, `ModeTransitionRequest`)?
2. Status: informative annex first, normative later?
3. Package naming and versioning of the published `.proto` files.

## References

1. [SISO-STD-018-2020, Space Reference FOM (SpaceFOM) 1.0](https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf)
2. [SpaceFOM 1.0 FOM modules (XML)](https://github.com/nasa/TrickHLA/tree/master/FOMs/SpaceFOM), as distributed in NASA TrickHLA
3. Möller, Karlsson et al., ["A Summary of Technical Updates in HLA 4 (IEEE 1516-2025)"](https://onearc.com/wp-content/uploads/2026/02/SISO_2026_SIW_028.pdf), SISO SIW 2026, paper 028
4. Crues, Möller, Garro, Dexter, ["SpaceFOM V2: The Next Generation in Space Simulation Interoperability and How You Can Help"](https://ntrs.nasa.gov/citations/20260008222), SISO SIMposium, Sept 2026
5. Möller et al., ["Evolving the SpaceFOM: Lessons Learned and Future Development"](https://ntrs.nasa.gov/api/citations/20250000915/downloads/SISO_2025_SIW_SpaceFOM_Paper.pdf), SISO SIW 2025
6. Crues, Dexter, Falcone, Garro, Möller, ["SpaceFOM – A robust standard for enabling a-priori interoperability of HLA-based space systems simulations"](https://doi.org/10.1080/17477778.2021.1945962), Journal of Simulation 16(6), 2022
7. SISO-ADM-003, *SISO Balloted Products Development and Support Process*, Appendix A (PCR form)
