# SpaceFOM Protobuf samples

Code generated from the SpaceFOM `.proto` schema in six languages, plus a small program and a test suite in each one. Every language decodes the same data files, written by the Python sample, to show that SpaceFOM data published once can be read anywhere.

| Language | Generated code | Sample and tests | Runtime library |
|---|---|---|---|
| C++ | [`generated/cpp`](generated/cpp) | [`cpp/`](cpp) (CMake, GoogleTest) | libprotobuf 36.2 |
| Python | [`generated/python`](generated/python) | [`python/`](python) (pytest) | `protobuf` 7.36.2 |
| Java | [`generated/java`](generated/java) | [`java/`](java) (Maven, JUnit) | `protobuf-java` 4.36.2 |
| C# | [`generated/csharp`](generated/csharp) | [`csharp/`](csharp) (.NET 10, xUnit) | `Google.Protobuf` 3.36.2 |
| TypeScript | [`generated/typescript`](generated/typescript) | [`typescript/`](typescript) (Node 26, `node:test`) | `@bufbuild/protobuf` 2.17.0 |
| Go | [`generated/go`](generated/go) | [`go/`](go) (`go test`) | `google.golang.org/protobuf` v1.36.12 |

The package names (`org.siso.spacefom.v1` in Java, `Siso.Spacefom.V1` in C#) are proposals. SISO has not published or approved them; see the [reference repository proposal](../proposal/reference-repository.md).

## How the pieces are produced

Two GitHub Actions workflows run one after the other. The first turns the FOM XML into `.proto` files. When those changes reach `main`, the second turns the `.proto` files into code for each language and tests it. Each workflow ends with a pull request that a person reviews and merges.

```mermaid
flowchart TD
    A["SpaceFOM FOM modules (XML)<br/>pinned in fom/SOURCE.json"] -->|"workflow 1: generate-proto<br/>generator/ (Python)"| B["proto/siso/spacefom/v1/*.proto<br/>+ field-number lock file"]
    B -->|"pull request, reviewed and merged"| M["main"]
    M -->|"workflow 2: generate-samples<br/>buf generate + samples/python/writer.py"| C["samples/generated/&lt;language&gt;/<br/>samples/data/*.binpb"]
    C --> T["build and test in C++, Python, Java,<br/>C#, TypeScript and Go"]
    T -->|"pull request, reviewed and merged"| M2["main"]
```

1. **[`generate-proto`](../.github/workflows/generate-proto.yml)** runs when `fom/`, `generator/` or its own file changes on `main`. It downloads the pinned FOM modules, runs the generator, validates the result (`protoc`, tests, `buf lint`, `buf breaking`) and opens a pull request that updates `proto/`.
2. **[`generate-samples`](../.github/workflows/generate-samples.yml)** runs when `proto/` or `samples/` changes. Merging the first pull request is such a change, so the second workflow follows on its own. It runs `buf generate` with [`buf.gen.yaml`](buf.gen.yaml), rewrites the data files, builds and tests all six languages in parallel, and opens a pull request that updates `samples/generated/` and `samples/data/`.

On a pull request, each workflow only checks: it fails if the committed files are out of date or a test fails. On branches other than `main`, it runs as a dry run and opens no pull request. You can also start either one by hand from the Actions tab, with a `dry_run` option.

## What the code does

- **[`buf.gen.yaml`](buf.gen.yaml)** lists one code generator per language. `protoc`'s built-in generators cover C++, Java, C# and Python; `protoc-gen-go` covers Go and `protoc-gen-es` covers TypeScript. Buf's managed mode adds the Java package and Go import path at generation time, so the `.proto` files carry no language-specific options.
- **[`python/writer.py`](python/writer.py)** builds five messages: a root and a child `ReferenceFrame`, a `DynamicalEntity`, an `ExecutionConfiguration` and a `ModeTransitionRequest`. It writes each one to [`data/`](data) as protobuf binary (`.binpb`), plus a `.json` copy you can read.
- **The readers** (`python/reader.py`, `go/main.go`, `typescript/reader.ts`, `java/src/main/java/Reader.java`, `csharp/Reader/Reader.cs`, `cpp/checks.cpp`) decode those files and check every value. They cover strings and doubles, the 9-element inertia matrix, enums, an empty `parent_name` that must still count as present, and an unset `torque` that must stay absent. The readers are short and look alike, so you can compare how each language handles the same message.
- **The tests** in each language run three kinds of check:
  - the reader checks above;
  - for each of the 18 generated message types, set every field, serialize, parse and compare (they find the types through protobuf reflection, so a missing type or field fails the test);
  - the enum values, including the `MTR_MODE_UNSPECIFIED = 0` value that the generator adds to `MTRMode`.

Two language details are worth knowing. C# drops an enum value's prefix when it matches the enum's name, so `MTR_MODE_UNSPECIFIED` becomes `MTRMode.Unspecified` while `MTR_GOTO_RUN` becomes `MTRMode.MtrGotoRun`. TypeScript code is generated as JavaScript plus `.d.ts` files, because Node runs TypeScript by stripping types and does not accept TypeScript `enum` declarations.

## Running it yourself

From the repository root, with protoc 36.2, buf, `protoc-gen-go` v1.36.12, Python 3.11+, Go, Node 26, Java 17+ with Maven, .NET 10+ and CMake installed:

```sh
(cd samples && npm ci)           # protoc-gen-es and the TypeScript runtime
pip install -r samples/python/requirements.txt
sh samples/test-all.sh           # regenerate, then build and test all six languages
```

To run one language, use the commands in [`test-all.sh`](test-all.sh). The C++ build uses an installed protobuf 36.2 if it finds one. Otherwise it builds protobuf from source, which takes a few minutes the first time. C++ needs this exact version, because protobuf requires "an exact match between the generated code version and the runtime version" for C++ ([cross-version runtime guarantee](https://protobuf.dev/support/cross-version-runtime-guarantee/)). The other languages accept a runtime of the same version or newer, up to the next major version.

Generated code is derived from the SpaceFOM FOM modules: Reprinted with permission from SISO Inc.
