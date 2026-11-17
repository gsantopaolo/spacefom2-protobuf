# Verification of technical claims

Every technical statement in the proposal was checked against a primary source. This table records where.

| Claim | Source |
|---|---|
| SpaceFOM uses Little Endian; only HLA logical time (`HLAinteger64Time`, underlying `HLAinteger64BE`) is Big Endian | SISO-STD-018-2020 §8.7.3 |
| Basic representations used: `HLAunicodeString`, `HLAinteger64Time`, `HLAinteger16LE`, `HLAfloat64LE` | SISO-STD-018-2020 §8.7.2.1 |
| All simple datatypes are `HLAfloat64LE`; `Time` is in seconds | SISO-STD-018-2020 Table 8-2, Table C-2 |
| SpaceFOM 1.0 defines no variant record datatypes | SISO-STD-018-2020 §8.7.2.6 |
| `ReferenceFrameTranslation` = `position: PositionVector`, `velocity: VelocityVector` | Table C-4; `SISO_SpaceFOM_datatypes.xml` |
| `ReferenceFrameRotation` = `attitude_quaternion: AttitudeQuaternion`, `angular_velocity: AngularVelocityVector` | Table C-5; `SISO_SpaceFOM_datatypes.xml` |
| `AttitudeQuaternion` = `scalar: Scalar`, `vector: Vector` (left unit transformation quaternion) | Table C-6; `SISO_SpaceFOM_datatypes.xml` |
| `SpaceTimeCoordinateState` = `translational_state`, `rotational_state`, `time: Time` (TT) | Table C-7; `SISO_SpaceFOM_datatypes.xml` |
| `ReferenceFrame` attributes = `name`, `parent_name`, `state`; root frame has empty `parent_name` | Table C-13 |
| `PhysicalEntity` attributes = `name`, `type`, `status`, `parent_reference_frame`, `state`, `acceleration`, `rotational_acceleration`, `center_of_mass`, `body_wrt_structural` | Table C-14 |
| `ExecutionMode`, `MTRMode` are `HLAinteger16LE` enumerations | Tables C-10, C-11 |
| FOM XML carries `<units>` on simple types and `<semantics>` on types and fields | `SISO_SpaceFOM_datatypes.xml` |
| HLA time stamp and lookahead are `HLAinteger64Time` in microseconds (1.0) | `SISO_SpaceFOM_datatypes.xml`, `<time>` |
| HLA 4 Federate Protocol: HLA services layer defined using Protobuf; transport TCP, TLS 1.3 or WebSockets | SISO SIW 2026-028 §2.1 |
| HLA 4 keeps HLA data encodings and adds `HLAextendableVariantRecord` | SISO SIW 2026-028 |
| In the Federate Protocol, attribute and parameter values are opaque `bytes` (`AttributeHandleValue.value`, `ParameterHandleValue.value`); Protobuf defines only the service envelope | IEEE 1516.1 Federate Protocol `datatypes.proto` (package `rti1516_2024.fedpro`, 2024 draft) as published in [HLA4FP open-source server](https://github.com/HLA4FP-Server-Project/Open-source-server-implementation-of-the-HLA4-Federate-Protocol), `src/main/proto/datatypes.proto`; same layout in the 2025 generated code of `@hla4ts/proto` 0.1.1 and VTMAK Python-Federate-Protocol. "Reprinted with permission from IEEE 1516.1(TM)-2024" |
| SpaceFOM 2.0 topics: configurable time resolution, epoch 2000, HLA 4 directed interactions and `Reference` datatype | SIMposium 2026 presentation, slides 17 and 19 |
| Proposed changes are collected as PCRs by the SpaceFOM PSG | SISO SIW 2025 SpaceFOM paper §3.4; SISO-ADM-003 Appendix A |

## Not yet verified

- The only public `.proto` source found is labelled the 2024 draft; the final IEEE 1516.1-2025 text (paywalled) was not checked. The 2025-labelled implementations show the same `bytes value = 2` layout in generated code.
- No source states in words that these bytes are HLA-encoded; that follows from the HLA encoding model rather than from the `.proto` text.
- Whether SISO-ADM-003-2011 is still the current PCR form.

FOM XML: SpaceFOM 1.0 modules as distributed in [nasa/TrickHLA](https://github.com/nasa/TrickHLA/tree/master/FOMs/SpaceFOM) (`SISO_SpaceFOM_datatypes.xml` last changed in commit `ed05f1b`, 2020-06-04).
