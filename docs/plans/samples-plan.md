# Plan: multi-language samples generated from the SpaceFOM `.proto`

Status: **approved** by the repo owner on 2026-11-17 and built in PR [#8](https://github.com/gsantopaolo/spacefom2-protobuf/pull/8). Decisions **[S1]…[S5]** are answered at the end.

## Goal

Show a vendor or tool builder that the generated schema works in their language. Each language gets code generated from `proto/siso/spacefom/v1/` and a small program that reads SpaceFOM data written by another language. The proposal claims exactly that cross-language read, so CI runs it for every language.

## Which languages, and why

I opened every source on 2026-11-17. Anything I could not check against a primary page is listed as unverified.

| # | Language | Likely SpaceFOM consumers | Code generation |
|---|---|---|---|
| 1 | C++ | TrickHLA and Trick models ([TrickHLA](https://github.com/nasa/TrickHLA), [Trick](https://nasa.github.io/trick/documentation/running_a_simulation/Input-File)); MAK RTI, "fully implemented in C++" ([MAK](https://www.mak.com/mak-one/tools/mak-rti/capabilities)); Portico and OpenRTI ([Portico](https://github.com/openlvc/portico), [OpenRTI](https://github.com/onox/OpenRTI)); ROS 2 `rclcpp` ([ROS 2 client libraries](https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/ROS-Framework/About-Client-Libraries.rst)); Unreal ([Epic](https://dev.epicgames.com/documentation/en-us/unreal-engine/programming-with-cplusplus-in-unreal-engine)); ESA SMP C++ headers ([ECSS-E-ST-40-07C](https://ecss.nl/standard/ecss-e-st-40-07c-rev-1-simulation-modelling-platform-level-1-5-august-2025/)) | `protoc --cpp_out` (built in) |
| 2 | Python | Trick input files; VTMAK's HLA 4 Federate Protocol client, which already uses protoc `_pb2` modules ([repo](https://github.com/VTMAK/Python-Federate-Protocol)); ROS 2 `rclpy`; Capella scripting ([Python4Capella](https://github.com/labs4capella/python4capella)); data analysis | `--python_out` and `--pyi_out` (built in) |
| 3 | Java | SpaceFOM tools in Java: SMASH-Lab HLA Development Kit for SEE ([repo](https://github.com/SMASH-Lab/HLA-Development-Kit)), Vega ([repo](https://github.com/atreia108/vega)); Portico; Kafka's maintained JVM client ([Kafka clients](https://cwiki.apache.org/confluence/display/KAFKA/Clients)); Capella and Cameo run on the JVM | `--java_out` (built in); Kotlin comes with `--kotlin_out` |
| 4 | C# | Unity ([Unity scripting](https://docs.unity.com/en-us/engine/current/manual/scripting)); Pitch Developer Studio generates C# ([OneArc](https://onearc.com/products/pitch-developer-tools/)); Kafka .NET | `--csharp_out` (built in) |
| 5 | TypeScript | CesiumJS ([repo](https://github.com/CesiumGS/cesium)) and web dashboards; Kafka and gRPC for Node | [protobuf-es](https://github.com/bufbuild/protobuf-es) (`protoc-gen-es`). Google's own JavaScript generator has "minimal support" ([repo](https://github.com/protocolbuffers/protobuf-javascript)) |
| 6 | Go | Cloud services, Kafka and gRPC clients | `protoc-gen-go`, Google's plugin ([Go guide](https://protobuf.dev/reference/go/go-generated/)) |
| 7 | Rust (optional) | Kafka and gRPC clients; ROS 2 community library | `protoc --rust_out`. The protobuf.dev support table does not list Rust, and the generated code needs an experimental flag (checked with protoc 36.2), so it would be marked preview |

Left out:
- Objective-C: support "will be dropped as of the 38.x release" ([version support](https://protobuf.dev/support/version-support/)).
- PHP, Ruby, Dart and Swift: no SpaceFOM consumer found.
- MATLAB: no general protobuf support found. MathWorks documents protobuf only in its Production Server Java and .NET clients ([MathWorks](https://www.mathworks.com/help/mps/java/struct-support-for-restful-requests-using-protocol-buffers-in-the-java-client.html)), so MATLAB users can call the Java sample.

Unverified: Pitch pRTI's language APIs (pitchtechnologies.com now redirects to onearc.com), MAK VR-Link languages, and which languages SpaceFOM PSG reference federates use.

Go and TypeScript need plugins; the others use protoc's built-in generators. With protoc 36.2, generation for C++, C#, Java, Kotlin, Python and Rust succeeds on the current `proto/`.

## Layout

```
samples/
  README.md                 the two-workflow pipeline, what the code does, how to run it
  buf.gen.yaml              one generation config for every language
  attribution.py            adds the SISO attribution to generated files that lack it
  test-all.sh               regenerate, then build and test every language locally
  data/                     shared data: one .binpb (and .json) per message
  python/                   writer.py, reader.py, test_samples.py (pytest)
  go/                       main.go (reader), main_test.go; go.mod is in samples/
  typescript/               reader.ts, reader.test.ts (node:test); package.json is in samples/
  java/                     Maven project: Reader.java, SamplesTest.java (JUnit)
  csharp/                   Reader/ (console app), Tests/ (xUnit)
  cpp/                      CMake project: checks.cpp, reader.cpp, samples_test.cpp (GoogleTest)
  generated/<language>/     generated code, committed ([S2])
```

`buf.gen.yaml` uses buf managed mode ([buf.gen.yaml v2](https://buf.build/docs/configuration/v2/buf-gen-yaml/)) to set `java_package`, `go_package` and similar options at generation time, so the `.proto` files carry no language options. **[S3]**

## What the samples do

- `python/writer.py` builds five messages: a root and a child `ReferenceFrame`, a `DynamicalEntity` (inherited and own attributes, including the 9-element inertia matrix), an `ExecutionConfiguration` and a `ModeTransitionRequest`. Each goes to its own file in `data/`, as `.binpb` plus a `.json` copy.
- Every reader decodes those files and checks the values: names, numbers with exact `double` equality, the enums, an empty `parent_name` that must still count as present, and an unset `torque` that must stay absent.
- Each reader then re-encodes one message and decodes its own output.

The readers compare values, not bytes, because protobuf serialization is not canonical across implementations.

## CI

A new workflow, `generate-samples.yml`, runs on changes to `proto/` or `samples/`:

1. One job regenerates the bindings (`buf generate`, then `attribution.py`) and the data (`writer.py`). On a pull request it fails if `samples/generated/` or `samples/data/` changed ([S2]). (Changed on 2026-11-17 by PR [#20](https://github.com/gsantopaolo/spacefom2-protobuf/pull/20) for [#19](https://github.com/gsantopaolo/spacefom2-protobuf/issues/19): a pull request that changes only the inputs now passes and the bot regenerates the output after the merge; a hand edit that does not match the generator still fails. See [`samples/README.md`](../../samples/README.md#how-the-pieces-are-produced).)
2. One matrix job per language sets up the toolchain, builds, runs the reader and runs the language's tests. The tests also round-trip each of the 18 message types with every field set, finding them through protobuf reflection.
3. On `main`, a last job opens a pull request with the regenerated files.

The generate-proto bot's pull request runs other workflows only after a maintainer approves them ([GitHub changelog, 11 June 2026](https://github.blog/changelog/2026-06-11-bot-created-pull-requests-can-run-workflows-if-approved/)), so the samples are not regenerated inside it. Instead, the second workflow runs once that pull request is merged into `main` and opens a follow-up pull request for the samples. **[S5]**

## Versions

Pin every plugin and runtime: protoc, `protoc-gen-go`, `protoc-gen-es` and the matching runtime libraries (`protobuf` for Python, `com.google.protobuf:protobuf-java`, `Google.Protobuf`, `@bufbuild/protobuf`, `google.golang.org/protobuf`). The exact versions are listed under Decisions.

## Phases

| Phase | Work |
|---|---|
| 1 | `buf.gen.yaml`, generation for the chosen languages, Python writer and data files |
| 2 | Readers and tests for C++, Python, Java, C#, TypeScript and Go |
| 3 | `generate-samples.yml` matrix workflow ([S5]) |
| 4 | `samples/README.md`, links from the main README; humanizer pass |

## Decisions

Answered by the repo owner on 2026-11-17.

| # | Decision |
|---|---|
| S1 | The six recommended languages: C++, Python, Java, C#, TypeScript, Go. No Rust for now |
| S2 | Commit the generated code under `samples/generated/`; CI fails if it is stale |
| S3 | Java package `org.siso.spacefom.v1`. Go import paths must be real repository paths, so Go uses `github.com/gsantopaolo/spacefom2-protobuf/samples/generated/go/...`. C# keeps protoc's default namespace `Siso.Spacefom.V1`. The samples README states that these names are proposals, not names published by SISO |
| S4 | Generated code, reader programs, tests, and the cross-language check in CI |
| S5 | Yes, as a second workflow (owner's direction, 2026-11-17). `generate-samples` runs when `proto/` changes on `main`, which is what merging the generate-proto pull request does. It regenerates the bindings and data, builds and tests all six languages, and opens its own pull request. The pipeline is described in [`samples/README.md`](../../samples/README.md) |

Versions follow protobuf's [cross-version runtime guarantee](https://protobuf.dev/support/cross-version-runtime-guarantee/): generated code is "never" paired with an older runtime, and C++ requires "an exact match between the generated code version and the runtime version". Everything is pinned to the protoc 36.2 release line: protoc 36.2, Python `protobuf` 7.36.2, `protobuf-java` 4.36.2, `Google.Protobuf` 3.36.2, libprotobuf 36.2 for C++, `protoc-gen-go` and `google.golang.org/protobuf` v1.36.12, and `@bufbuild/protoc-gen-es` with `@bufbuild/protobuf` 2.17.0.
