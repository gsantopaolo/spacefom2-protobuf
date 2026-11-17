# Plan: multi-language samples generated from the SpaceFOM `.proto`

Status: **approved** by the repo owner on 2026-11-17. Decisions **[S1]…[S5]** are answered at the end.

## Goal

Show a vendor or tool builder that the generated schema works in their language. For each language this means two things: code generated from `proto/siso/spacefom/v1/`, and a small program that reads SpaceFOM data written by another language. That cross-language read is the claim the proposal makes, so the samples should prove it in CI rather than only ship generated files.

## Which languages, and why

Sources were opened on 2026-11-17. Claims marked *unverified* could not be checked against a primary page.

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

All languages except Go and TypeScript generate with protoc's built-in generators. I checked that C++, C#, Java, Kotlin, Python and Rust generation all succeed on the current `proto/` with protoc 36.2.

## Layout

```
samples/
  README.md                 the two-workflow pipeline, what the code does, how to run it
  buf.gen.yaml              one generation config for every language
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

`buf.gen.yaml` uses buf managed mode ([buf.gen.yaml v2](https://buf.build/docs/configuration/v2/buf-gen-yaml/)) to set `java_package`, `go_package` and similar options at generation time. The `.proto` files themselves stay free of language options. **[S3]**

## What the samples do

- `python/writer.py` builds one `ReferenceFrame` (a root frame and a child frame), one `DynamicalEntity` (inherited plus own attributes, including the 9-element inertia matrix) and one `ExecutionConfiguration` (with an enum value). It writes them as length-delimited messages to `data/entities.binpb`.
- Every `reader` decodes that file and prints the values. It then checks them against the expected values: names, numbers with exact `double` equality, the enum, and that `parent_name` is present and empty for the root frame, which tests `optional` presence.
- Each reader also re-encodes the messages and decodes its own output, to show the round trip.

Byte-for-byte equality across languages is not checked. Protobuf serialization is not canonical, so value equality is the right test.

## CI

A new workflow, `generate-samples.yml`, runs on changes to `proto/` or `samples/`:

1. Regenerate with `buf generate` and fail if `samples/generated/` changed ([S2]).
2. One matrix job per language: set up the toolchain, build, run the reader, and run the language's tests. The tests also round-trip every one of the 18 message types with all fields set, found through protobuf reflection.
3. The Python job also regenerates the fixture and checks it is unchanged.

The generate-proto bot's pull request does not trigger other workflows, so the samples cannot be checked inside it. Instead, the second workflow runs once that pull request is merged into `main` and opens a follow-up pull request for the samples. **[S5]**

## Versions

Pin every plugin and runtime: protoc, `protoc-gen-go`, `protoc-gen-es` and the matching runtime libraries (`protobuf` for Python, `com.google.protobuf:protobuf-java`, `Google.Protobuf`, `@bufbuild/protobuf`, `google.golang.org/protobuf`). The exact versions are listed under Decisions.

## Phases

| Phase | Work |
|---|---|
| 1 | `buf.gen.yaml`, generation for the chosen languages, Python writer and fixture |
| 2 | Readers for C++, Java, C#, TypeScript, Go (and Rust if chosen) |
| 3 | `samples.yml` matrix workflow; generate-proto update ([S5]) |
| 4 | `samples/README.md`, links from the main README and technical overview; humanizer pass |

## Decisions

Answered by the repo owner on 2026-11-17.

| # | Decision |
|---|---|
| S1 | The six recommended languages: C++, Python, Java, C#, TypeScript, Go. No Rust for now |
| S2 | Commit the generated code under `samples/generated/`; CI fails if it is stale |
| S3 | Java package `org.siso.spacefom.v1`. Go import paths must be real repository paths, so Go uses `github.com/gsantopaolo/spacefom2-protobuf/samples/generated/go/...`. C# keeps protoc's default namespace `Siso.Spacefom.V1`. The samples README states that these names are proposals, not names published by SISO |
| S4 | Generated code, plus the reader programs and the CI interop test |
| S5 | Yes, as a second workflow (owner's direction, 2026-11-17). `generate-samples` runs when `proto/` changes on `main`, which is what merging the generate-proto pull request does. It regenerates the bindings and data, builds and tests all six languages, and opens its own pull request. The pipeline is described in [`samples/README.md`](../../samples/README.md) |

Versions follow protobuf's [cross-version runtime guarantee](https://protobuf.dev/support/cross-version-runtime-guarantee/): generated code is "never" paired with an older runtime, and C++ requires "an exact match between the generated code version and the runtime version". Everything is pinned to the protoc 36.2 release line: protoc 36.2, Python `protobuf` 7.36.2, `protobuf-java` 4.36.2, `Google.Protobuf` 3.36.2, libprotobuf 36.2 for C++, `protoc-gen-go` and `google.golang.org/protobuf` v1.36.12, and `@bufbuild/protoc-gen-es` with `@bufbuild/protobuf` 2.17.0.
