# Verification of technical claims

Every technical statement in the proposal was checked against the primary source listed next to it. PDF links open at the cited page; XML and `.proto` links point to the exact lines in a pinned commit.

| Claim | Source |
|---|---|
| SpaceFOM uses Little Endian; only HLA logical time (`HLAinteger64Time`, underlying `HLAinteger64BE`) is Big Endian | [SISO-STD-018-2020 §8.7.3][std103] |
| Basic representations used: `HLAunicodeString`, `HLAinteger64Time`, `HLAinteger16LE`, `HLAfloat64LE` | [SISO-STD-018-2020 §8.7.2.1][std101] |
| All simple datatypes are `HLAfloat64LE`; `Time` is in seconds | [SISO-STD-018-2020 Table 8-2][std102], [Table C-2][std124] |
| SpaceFOM 1.0 defines no variant record datatypes | [SISO-STD-018-2020 §8.7.2.6][std103] |
| `ReferenceFrameTranslation` = `position: PositionVector`, `velocity: VelocityVector` | [Table C-4][std127]; [`SISO_SpaceFOM_datatypes.xml` L311–324][xml-rft] |
| `ReferenceFrameRotation` = `attitude_quaternion: AttitudeQuaternion`, `angular_velocity: AngularVelocityVector` | [Table C-5][std127]; [`SISO_SpaceFOM_datatypes.xml` L326–339][xml-rfr] |
| `AttitudeQuaternion` = `scalar: Scalar`, `vector: Vector` (left unit transformation quaternion) | [Table C-6][std127]; [`SISO_SpaceFOM_datatypes.xml` L341–354][xml-aq] |
| `SpaceTimeCoordinateState` = `translational_state`, `rotational_state`, `time: Time` (TT) | [Table C-7][std128]; [`SISO_SpaceFOM_datatypes.xml` L356–374][xml-stcs] |
| `ReferenceFrame` attributes = `name`, `parent_name`, `state`; root frame has empty `parent_name` | [Table C-13][std133] |
| `PhysicalEntity` attributes = `name`, `type`, `status`, `parent_reference_frame`, `state`, `acceleration`, `rotational_acceleration`, `center_of_mass`, `body_wrt_structural` | [Table C-14][std134] |
| `ExecutionMode`, `MTRMode` are `HLAinteger16LE` enumerations | [Tables C-10, C-11][std130] |
| FOM XML carries `<units>` on simple types and `<semantics>` on types and fields | [`SISO_SpaceFOM_datatypes.xml` L67–224][xml-units] |
| HLA time stamp and lookahead are `HLAinteger64Time` in microseconds (1.0) | [`SISO_SpaceFOM_datatypes.xml` L55–64][xml-time] |
| HLA 4 Federate Protocol: HLA services layer defined using Protobuf; transport TCP, TLS 1.3 or WebSockets | [SISO SIW 2026-028 §2.1][siw26-p4] |
| HLA 4 keeps HLA data encodings and adds `HLAextendableVariantRecord` | [SISO SIW 2026-028][siw26-p6] |
| In the Federate Protocol, attribute and parameter values are opaque `bytes`; Protobuf defines only the service envelope | IEEE 1516.1 Federate Protocol `datatypes.proto` (package `rti1516_2024.fedpro`, 2024 draft): [`AttributeHandleValue` L167–170][fp-ahv], [`ParameterHandleValue` L178–181][fp-phv], as published in the [HLA4FP open-source server][fp-repo]. Same layout in the 2025 generated code of [`@hla4ts/proto` 0.1.1][hla4ts] and [VTMAK Python-Federate-Protocol][vtmak]. "Reprinted with permission from IEEE 1516.1(TM)-2024" |
| SpaceFOM 2.0 topics: configurable time resolution, epoch 2000, HLA 4 directed interactions and `Reference` datatype | SIMposium 2026 presentation, [slide 17][sim17] and [slide 19][sim19] |
| Proposed changes are collected as PCRs by the SpaceFOM PSG | [SISO SIW 2025 SpaceFOM paper §3.4][siw25-p7]; [SISO-ADM-003 Appendix A][adm-a] |

## Not yet verified

- The only public `.proto` source found is labelled the 2024 draft; the final IEEE 1516.1-2025 text (paywalled) was not checked. The 2025-labelled implementations show the same `bytes value = 2` layout in generated code.
- No source states in words that these bytes are HLA-encoded; that follows from the HLA encoding model rather than from the `.proto` text.
- Whether [SISO-ADM-003-2011][adm] is still the current PCR form.

FOM XML: SpaceFOM 1.0 modules as distributed in [nasa/TrickHLA][trickhla]; links are pinned to commit [`ed05f1b`][xml-commit] (2020-06-04), the last change to `SISO_SpaceFOM_datatypes.xml`.

[std]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf
[std101]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=101
[std102]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=102
[std103]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=103
[std124]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=124
[std127]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=127
[std128]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=128
[std130]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=130
[std133]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=133
[std134]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf#page=134
[trickhla]: https://github.com/nasa/TrickHLA/tree/master/FOMs/SpaceFOM
[xml-commit]: https://github.com/nasa/TrickHLA/commit/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b
[xml-time]: https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L55-L64
[xml-units]: https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L67-L224
[xml-rft]: https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L311-L324
[xml-rfr]: https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L326-L339
[xml-aq]: https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L341-L354
[xml-stcs]: https://github.com/nasa/TrickHLA/blob/ed05f1b2f0bada22fffe12c1d5d5b551bbcfa91b/FOMs/SpaceFOM/SISO_SpaceFOM_datatypes.xml#L356-L374
[siw26-p4]: https://onearc.com/wp-content/uploads/2026/02/SISO_2026_SIW_028.pdf#page=4
[siw26-p6]: https://onearc.com/wp-content/uploads/2026/02/SISO_2026_SIW_028.pdf#page=6
[fp-repo]: https://github.com/HLA4FP-Server-Project/Open-source-server-implementation-of-the-HLA4-Federate-Protocol
[fp-ahv]: https://github.com/HLA4FP-Server-Project/Open-source-server-implementation-of-the-HLA4-Federate-Protocol/blob/974eab4436289e1af16f432e7955400ee20d4766/src/main/proto/datatypes.proto#L167-L170
[fp-phv]: https://github.com/HLA4FP-Server-Project/Open-source-server-implementation-of-the-HLA4-Federate-Protocol/blob/974eab4436289e1af16f432e7955400ee20d4766/src/main/proto/datatypes.proto#L178-L181
[hla4ts]: https://www.npmjs.com/package/@hla4ts/proto
[vtmak]: https://github.com/VTMAK/Python-Federate-Protocol
[sim17]: https://ntrs.nasa.gov/api/citations/20260008222/downloads/2026_simposium_SpaceFOM_EZC.pdf#page=17
[sim19]: https://ntrs.nasa.gov/api/citations/20260008222/downloads/2026_simposium_SpaceFOM_EZC.pdf#page=19
[siw25-p7]: https://ntrs.nasa.gov/api/citations/20250000915/downloads/SISO_2025_SIW_SpaceFOM_Paper.pdf#page=7
[adm]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/admin_products_/siso-adm-003-2011_ew_changes.pdf
[adm-a]: https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/admin_products_/siso-adm-003-2011_ew_changes.pdf#page=54
