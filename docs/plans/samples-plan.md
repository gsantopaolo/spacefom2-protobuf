# Plan: multi-language samples generated from the SpaceFOM `.proto`

Status: **draft for review**. Decisions are marked **[S1]…[S5]** and collected at the end.

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
  README.md                 what each sample shows, how to run it
  buf.gen.yaml              one generation config for every language
  data/
    entities.binpb          shared wire fixture: ReferenceFrame, DynamicalEntity, ExecutionConfiguration
    entities.json           the same values in protobuf JSON, for humans
  python/   writer.py, reader.py
  cpp/      reader.cpp, CMakeLists.txt
  java/     Reader.java, build file
  csharp/   Reader.cs, .csproj
  typescript/ reader.ts, package.json
  go/       reader.go, go.mod
  generated/<language>/     generated code (if committed, [S2])
```

`buf.gen.yaml` uses buf managed mode ([buf.gen.yaml v2](https://buf.build/docs/configuration/v2/buf-gen-yaml/)) to set `java_package`, `go_package` and similar options at generation time. The `.proto` files themselves stay free of language options. **[S3]**

## What the samples do

- `python/writer.py` builds one `ReferenceFrame` (a root frame and a child frame), one `DynamicalEntity` (inherited plus own attributes, including the 9-element inertia matrix) and one `ExecutionConfiguration` (with an enum value). It writes them as length-delimited messages to `data/entities.binpb`.
- Every `reader` decodes that file and prints the values. It then checks them against the expected values: names, numbers with exact `double` equality, the enum, and that `parent_name` is present and empty for the root frame, which tests `optional` presence.
- Each reader also re-encodes the messages and decodes its own output, to show the round trip.

Byte-for-byte equality across languages is not checked. Protobuf serialization is not canonical, so value equality is the right test.

## CI

A new workflow, `samples.yml`, runs on changes to `proto/` or `samples/`:

1. Regenerate with `buf generate` and fail if `samples/generated/` changed ([S2]).
2. One matrix job per language: set up the toolchain, build, and run the reader against the committed fixture.
3. The Python job also regenerates the fixture and checks it is unchanged.

Because the generate-proto bot opens a PR when the schema changes and that PR does not trigger other workflows, the generate-proto job also needs to run `buf generate` for the samples. Otherwise the generated sample code goes stale in the bot PR. **[S5]**

## Versions

Pin every plugin and runtime: protoc, `protoc-gen-go`, `protoc-gen-es` and the matching runtime libraries (`protobuf` for Python, `com.google.protobuf:protobuf-java`, `Google.Protobuf`, `@bufbuild/protobuf`, `google.golang.org/protobuf`). Generated code and runtime library versions have to be compatible. I have not yet read the exact rule in protobuf's [cross-version runtime guarantee](https://protobuf.dev/support/cross-version-runtime-guarantee/); I'll check it in phase 1 before choosing pins.

## Phases

| Phase | Work |
|---|---|
| 1 | `buf.gen.yaml`, generation for the chosen languages, Python writer and fixture |
| 2 | Readers for C++, Java, C#, TypeScript, Go (and Rust if chosen) |
| 3 | `samples.yml` matrix workflow; generate-proto update ([S5]) |
| 4 | `samples/README.md`, links from the main README and technical overview; humanizer pass |

## Decisions

- **S1** Languages: the six recommended (C++, Python, Java, C#, TypeScript, Go), or also Rust as preview?
- **S2** Commit the generated code under `samples/generated/` so vendors can browse it, or generate it only in CI and locally?
- **S3** Package names for languages that need them: Java `io.github.gsantopaolo.spacefom.v1`, Go module `github.com/gsantopaolo/spacefom2-protobuf/samples/generated/go`, C# namespace `Siso.Spacefom.V1` (protoc's default from the package)? A `org.siso…` Java package would suggest SISO publishes it, so I'd avoid it.
- **S4** Depth: generated code only, or generated code plus the cross-language reader programs and the CI interop test described above?
- **S5** Should the generate-proto workflow also regenerate the sample code, so its bot PR stays consistent?
