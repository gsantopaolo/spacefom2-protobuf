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
| `MTRMode` values are 2, 3, 4 (no 0); `ExecutionMode` starts at `EXEC_MODE_UNINITIALIZED = 0` | [`SISO_SpaceFOM_management.xml` L227–268][xml-enums] |
| `DynamicalEntity` is nested inside `PhysicalEntity` in the FOM (a subclass), so the generator flattens it | [`SISO_SpaceFOM_entity.xml` L172–242][xml-dyn] |
| `ExecutionConfiguration.least_common_time_step` is `HLAinteger64Time` | [`SISO_SpaceFOM_management.xml` L143–147][xml-lcts] |
| proto3: the first enum value must be zero; field numbers 19,000–19,999 are reserved for the implementation; a field number "cannot be changed once your message type is in use" and "should never be reused" | [Protobuf proto3 language guide][proto3] |
| buf `STANDARD` lint flags the FOM's enum names under `ENUM_VALUE_PREFIX` and `ENUM_ZERO_VALUE_SUFFIX`, and nothing else in the generated files | [buf lint rules][buf-lint]; run locally with buf 1.75.0 on 2026-11-17 |
| `buf.yaml` v2 keys `modules.path`, `lint.use`/`except` and `breaking.use`; `WIRE` breaking category | [buf.yaml v2 reference][buf-yaml]; [buf breaking rules][buf-breaking] |
| The "Run workflow" button for `workflow_dispatch` appears only when the workflow file is on the default branch | [GitHub Docs, events that trigger workflows][gh-events] |
| Events triggered with `GITHUB_TOKEN` do not start new workflow runs (except `workflow_dispatch` and `repository_dispatch`), so the generator job validates before it opens the PR | [GitHub Docs, triggering a workflow][gh-trigger] |
| Action inputs used: `create-pull-request` v8.1.3 (`branch`, `delete-branch`, `add-paths`, `body-path`), `buf-action` v1.7.0 (`setup_only`), `setup-python` v7.1.0 (`cache`, `cache-dependency-path`) | `action.yml` at each tag: [create-pull-request][cpr-action], [buf-action][buf-action], [setup-python][sp-action] |
| Protobuf generated code must "never" run on a runtime older than the protoc that generated it; C++ and Rust require "an exact match between the generated code version and the runtime version" | [Protobuf cross-version runtime guarantee][xver] |
| Languages built into `protoc`: C++, C#, Java, Kotlin, Objective-C, PHP, Python, Ruby; Go and Dart use Google-supported plugins | [Protobuf overview][pb-overview] |
| protobuf-es generates TypeScript/JavaScript; Google's protobuf-javascript has "minimal support" | [protobuf-es][pb-es]; [protobuf-javascript][pb-js] |
| The sample languages' consumers (TrickHLA and Trick in C++ and Python, Java SpaceFOM tools, Unity in C#, CesiumJS) | Sources listed in [`docs/plans/samples-plan.md`](plans/samples-plan.md#which-languages-and-why) |
| buf managed mode sets `java_package` and `go_package` at generation time; `protoc_builtin` and `local` plugin keys | [buf.gen.yaml v2 reference][buf-gen] |
| C# generated enum values drop the enum-name prefix (`MTR_MODE_UNSPECIFIED` → `MTRMode.Unspecified`) | Generated code: `samples/generated/csharp/Management.cs`, protoc 36.2 |
| Node runs TypeScript by stripping types and rejects `enum` ("TypeScript enum is not supported in strip-only mode"), so TypeScript is generated as JavaScript plus `.d.ts` | Node 26.13.1 error output, local run on 2026-11-17 |
| `create-pull-request` v8.1.3 applies `labels` with a separate `issues.addLabels` call after the PR is created; GitHub's "Add labels to an issue" docs do not say whether a missing label is created, and list `422 Validation failed` among the responses. The workflows therefore set no labels | [`src/github-helper.ts` L239–246 at v8.1.3][cpr-labels]; [GitHub REST, Add labels to an issue][gh-labels] |
| Each action is pinned to the commit its release tag points to (annotated tags dereferenced), resolved through the GitHub API on 2026-11-17: checkout v7.0.1, setup-python v7.1.0, buf-action v1.7.0, upload-artifact v7.0.2, download-artifact v8.0.2, create-pull-request v8.1.3 | `GET /repos/{owner}/{repo}/git/ref/tags/{tag}` for each action |

## Not yet verified

- The only public `.proto` source found is labelled the 2024 draft; the final IEEE 1516.1-2025 text (paywalled) was not checked. The 2025-labelled implementations show the same `bytes value = 2` layout in generated code.
- No source states in words that these bytes are HLA-encoded; that follows from the HLA encoding model rather than from the `.proto` text.
- Whether [SISO-ADM-003-2011][adm] is still the current PCR form.

FOM XML: SpaceFOM 1.0 modules as distributed in [nasa/TrickHLA][trickhla]; links are pinned to commit [`ed05f1b`][xml-commit] (2020-06-04), the last change to `SISO_SpaceFOM_datatypes.xml`. Links to the entity and management modules are pinned to [`1677fd0`][fom-commit] (2025-12-02), the commit the generator downloads (see `fom/SOURCE.json`). The four files at that commit have the sha256 values recorded there.

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
[fom-commit]: https://github.com/nasa/TrickHLA/commit/1677fd0e0e3ff45d6bff712169c463e38ede5586
[xml-enums]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/FOMs/SpaceFOM/SISO_SpaceFOM_management.xml#L227-L268
[xml-lcts]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/FOMs/SpaceFOM/SISO_SpaceFOM_management.xml#L143-L147
[xml-dyn]: https://github.com/nasa/TrickHLA/blob/1677fd0e0e3ff45d6bff712169c463e38ede5586/FOMs/SpaceFOM/SISO_SpaceFOM_entity.xml#L172-L242
[proto3]: https://protobuf.dev/programming-guides/proto3/
[buf-lint]: https://buf.build/docs/lint/rules/
[buf-yaml]: https://buf.build/docs/configuration/v2/buf-yaml/
[buf-breaking]: https://buf.build/docs/breaking/rules/
[gh-events]: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
[gh-trigger]: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
[cpr-action]: https://github.com/peter-evans/create-pull-request/blob/v8.1.3/action.yml
[buf-action]: https://github.com/bufbuild/buf-action/blob/v1.7.0/action.yml
[sp-action]: https://github.com/actions/setup-python/blob/v7.1.0/action.yml
[xver]: https://protobuf.dev/support/cross-version-runtime-guarantee/
[pb-overview]: https://protobuf.dev/overview/
[pb-es]: https://github.com/bufbuild/protobuf-es
[pb-js]: https://github.com/protocolbuffers/protobuf-javascript
[buf-gen]: https://buf.build/docs/configuration/v2/buf-gen-yaml/
[cpr-labels]: https://github.com/peter-evans/create-pull-request/blob/3ffccacd46053766916f087ce41d627c0b8cf2d1/src/github-helper.ts#L239-L246
[gh-labels]: https://docs.github.com/en/rest/issues/labels#add-labels-to-an-issue
