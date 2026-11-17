# Plan: FOM XML → `.proto` generator with CI

Status: **draft for review**. Nothing here is built yet. Decisions you need to make are marked **[D1]…[D8]** and collected in §9.

Bracketed numbers like [S3] point to the Sources list at the end. Facts about the FOM come from the five XML files in `reference-docs/standards/fom-xml-trickhla/`. I checked those files byte for byte against `nasa/TrickHLA` `master` on 2026-11-17 and they are identical.

## Contents

1. [What the input actually contains](#1-what-the-input-actually-contains)
2. [Repo layout](#2-repo-layout)
3. [Generator design](#3-generator-design)
4. [Stable field numbering (the main technical risk)](#4-stable-field-numbering-the-main-technical-risk)
5. [Validation](#5-validation-runs-in-ci-before-any-pr-is-opened)
6. [GitHub Action](#6-github-action-githubworkflowsgenerate-protoyml)
7. [Getting the FOM XML into the repo, and the license question](#7-getting-the-fom-xml-into-the-repo-and-the-license-question)
8. [Phased tasks](#8-phased-tasks-rough-effort)
9. [Decisions for you](#9-decisions-for-you)
- [Sources](#sources)

## 1. What the input actually contains

| Module | What the generator needs from it |
|---|---|
| `SISO_SpaceFOM_datatypes.xml` | `<time>` (`HLAinteger64Time`, "Microseconds since the beginning of the federation execution"). Also 20 `simpleData` (all `HLAfloat64LE`, each with `<units>` such as `meter (m)` or `radian per second (r/s)`), 11 `arrayData` (cardinality 3 or 9) and 4 `fixedRecordData` |
| `SISO_SpaceFOM_environment.xml` | Object class `ReferenceFrame` (`name`, `parent_name`, `state`) |
| `SISO_SpaceFOM_entity.xml` | `PhysicalEntity` and its **nested subclass** `DynamicalEntity`, plus `PhysicalInterface` |
| `SISO_SpaceFOM_management.xml` | 2 `enumeratedData` (`ExecutionMode`, `MTRMode`, both `HLAinteger16LE`), object class `ExecutionConfiguration` and interaction `ModeTransitionRequest` |
| `SISO_SpaceFOM_switches.xml` | RTI switches only. Ignored |

Things the mapping table in `technical-overview.md` does not cover yet:
- **`MTRMode` has no value 0.** Its values start at `MTR_GOTO_RUN = 2`, and proto3 requires the first enum value to be zero [S9]. I confirmed this with local `protoc` 36.2, which reports "The first enum value must be zero for open enums." The generator has to add a value such as `MTR_MODE_UNSPECIFIED = 0`. **[D4]**
- **Enum value names in the FOM do not follow buf `STANDARD` lint.** `EXEC_MODE_*` is not prefixed with `EXECUTION_MODE_`, and neither enum has an `_UNSPECIFIED` zero value. Lint would flag both (`ENUM_VALUE_PREFIX`, `ENUM_ZERO_VALUE_SUFFIX`) [S13]. Enum values share one namespace across sibling enums [S10], so keeping the FOM's own prefixes is still collision-free today. **[D4]**
- **Inheritance.** For `DynamicalEntity ⊂ PhysicalEntity`, the proposal is to flatten: the subclass message repeats the parent's attributes first, in FOM order, then its own.
- `ExecutionConfiguration.least_common_time_step` is `HLAinteger64Time`, so it maps to `int64`.
- TrickHLA also ships `SISO_SpaceFOM_management2.xml` ("Augmented Management", dated 2023-07-14, adds `ExecutionConfiguration2`). It is a TrickHLA extension, not part of SISO-STD-018-2020. Proposal: exclude it. **[D3]**

## 2. Repo layout

```
fom/
  SOURCE.json            provenance: upstream repo, commit SHA, path, sha256 of each file, retrieval date
  *.xml                  (only if vendored; see §7 / [D1])
generator/
  spacefom_proto/        package: parse.py, model.py, mapping.py, emit.py, ids.py
  field-ids.lock.json    stable field-number map (see §4)
  tests/                 unit tests and the golden test
proto/siso/spacefom/v1/  generated output (directory matches the package, per buf PACKAGE_DIRECTORY_MATCH [S13])
  datatypes.proto  environment.proto  entity.proto  management.proto
history/<UTC-timestamp>_<fom-sha7>/   archived previous proto/ trees (§6)
buf.yaml
.github/workflows/generate-proto.yml
```

One `.proto` per FOM module, all in package `siso.spacefom.v1`, with imports between them. **[D2]** The alternative is a single `spacefom.proto`. Buf's default `FILE` breaking category flags moving a type from one file to another [S11], so the choice is hard to change later.

## 3. Generator design

- **Parsing:** use Python 3 stdlib `xml.etree.ElementTree` with a namespace map for `http://standards.ieee.org/IEEE1516-2010`. `findall()` returns elements in document order [S14], which is what makes field order deterministic. The Python docs point to the XML security notes for untrusted data [S14]. Our only input is our own pinned files, so `defusedxml` is optional. No third-party dependency is needed for parsing.
- **Model:** build an intermediate model (types, records, arrays, enums, object classes, interactions) with name resolution across modules. The generator fails loudly on an unknown `dataType`, an unsupported encoding (anything not in the mapping table, such as variant records) or a name collision.
- **Mapping:** follow the table in `docs/technical-overview.md`:
  - simple types become `double`, with the unit as a comment;
  - `HLAinteger64Time` becomes `int64`;
  - `HLAunicodeString` becomes `string`;
  - a fixed array of 3 becomes a message with `x`, `y`, `z`;
  - a fixed array of 9 becomes `repeated double`, with "9 elements, row-wise" in a comment;
  - a fixed record becomes a message, keeping field order;
  - object-class attributes are all `optional`;
  - `<semantics>` becomes a comment (word-wrapped, otherwise verbatim).
- **Interactions:** whether to emit them is **[D5]**. The proposal is a generator flag that defaults to on, because there is only one interaction (`ModeTransitionRequest`).
- **Deterministic output:**
  - no timestamps or absolute paths inside the `.proto` files;
  - LF line endings and a fixed indentation and wrap width;
  - declaration order follows FOM document order, modules processed in a fixed order;
  - the file header records the generator version and the sha256 of each input file.

  The same input therefore always produces identical bytes, which is what makes "did the output change?" a plain `git diff`.
- **Attribution header** in every generated file: "Derived from SISO-STD-018-2020 FOM modules. Reprinted with permission from SISO Inc." (see §7).

## 4. Stable field numbering (the main technical risk)

Protobuf identifies fields on the wire by number. A field number "cannot be changed once your message type is in use" and "should never be reused". A deleted field's number must be `reserved` [S9]. Deriving numbers from FOM position would silently corrupt data whenever a 2.0 module inserts or removes an attribute: old consumers would decode new bytes into the wrong fields.

The strategy is a committed lock file, `generator/field-ids.lock.json`:
- It maps `Message.field` to a number. On the first run, numbers are assigned in FOM order starting at 1, which reproduces the hand-written example.
- A new field gets `max(used ∪ retired) + 1`. Existing fields keep their numbers even if FOM order changes. Numbers 19000–19999 are skipped [S9].
- A removed field moves to `retired` and is emitted as `reserved <n>; reserved "<name>";`.
- **A rename in the FOM looks like delete + add.** The generator cannot tell the two apart. It emits a new number and the PR body lists the case under "needs human review". An optional `renames` section in the lock file lets a reviewer keep the old number. **[D6]**
- Enum values use the FOM's own values, so they need no lock entries. Only the synthetic zero value is generator-defined.
- The lock file is updated in the same PR as the `.proto` files, so reviewers see every new or retired number.

## 5. Validation (runs in CI before any PR is opened)

1. **Unit tests** (pytest) for parsing and mapping, using small fixture XMLs.
2. **Compile:** run `protoc` over `proto/` with `--descriptor_set_out`. I checked the flags in the local `protoc 36.2 --help`. For CI, use `python -m grpc_tools.protoc` from `grpcio-tools` [S15] so there is no separate protoc install. Alternatively, download a pinned protoc release [S16].
3. **Golden test against `docs/examples/reference_frame.proto`:**
   - The comparison has to be **structural**, because a text diff would fail on comments: the example's comments are hand-written ("empty for the root frame", `rad/s`), while the FOM says `radian per second (r/s)`.
   - Compile both files to descriptor sets without `--include_source_info`, which strips comments (`protoc --help`). Then assert that every message in the example exists in the generated output with identical field names, numbers, types and labels.
   - The example compiles with `protoc` today (checked locally).
4. **Idempotence check:** regenerate a second time, and require identical bytes and no change to the lock file.
5. **buf:** run `buf lint` and `buf breaking --against '.git#branch=main,subdir=proto'` [S12]. Use breaking category **`WIRE`** (wire compatibility is what matters to consumers) rather than the default `FILE` [S11].
   - Lint needs exceptions for FOM-faithful enum names (§1, [D4]).
   - Install buf via `bufbuild/buf-action@v1` with `setup_only: true` [S6][S7]. No BSR token is needed when nothing is pushed: the token is only "required for push and label-archive steps" [S7].

## 6. GitHub Action: `.github/workflows/generate-proto.yml`

**Triggers (proposed):**
- `workflow_dispatch`, for on-demand runs. It supports inputs [S3], for example `dry_run`.
- `push` to `main` with `paths:` `fom/**`, `generator/**` and the workflow file [S3]. Merging a generated PR changes `proto/` and `history/`, which are not in the filter. The workflow is idempotent anyway, so it would be a no-op.
- `pull_request` with the same paths, in **check mode** only: regenerate, validate, and fail if the committed `proto/` is stale. It never opens a PR.
- Optional `schedule` (weekly) that checks whether TrickHLA's FOM files changed upstream and opens a PR updating `fom/SOURCE.json`. **[D7]**

**Generate job steps:**
1. `actions/checkout` (latest v7.0.1 [S17]).
2. `actions/setup-python` (latest v7.1.0 [S17]).
3. Install the pinned dependencies (`grpcio-tools`, `pytest`).
4. If not vendored, fetch the FOM XML at the commit pinned in `fom/SOURCE.json` and verify the sha256 values.
5. Copy the current `proto/` to a temp directory, then run the generator, which writes `proto/` and the lock file.
6. Run the validation from §5. **Validation must pass here, inside this job:** a PR opened with the default `GITHUB_TOKEN` does not trigger `pull_request` workflows. "Events triggered by the `GITHUB_TOKEN` will not create a new workflow run" except `workflow_dispatch` and `repository_dispatch` [S4][S5].
7. `git diff --quiet -- proto/ generator/field-ids.lock.json`. If nothing changed, stop.
8. Otherwise, move the temp copy into `history/<UTC-timestamp>_<fom-sha7>/` and add a `MANIFEST.json` (previous FOM sha256 values, generator version, the source commit of `main`).
9. Open the PR with `peter-evans/create-pull-request@v8`, pinned to v8.1.3, the latest release [S1][S17]:
   - fixed `branch: generator/proto-update`, so later runs update the same PR rather than opening new ones [S1];
   - `add-paths: proto/, history/, generator/field-ids.lock.json`;
   - `delete-branch: true`;
   - labels `generated`;
   - `body` with a summary of added, removed and renamed fields and new or retired numbers.

   If there is no diff, the action "exits silently" [S1].

**Permissions:**
- Workflow `permissions: contents: write, pull-requests: write` [S1][S2].
- The repo setting **Settings → Actions → General → Workflow permissions → "Allow GitHub Actions to create and approve pull requests"** must be enabled. It is off by default for personal-account repos [S8].
- Add `concurrency: { group: generate-proto, cancel-in-progress: false }` [S3] so two runs never race on the PR branch.
- **[D8]** If you want CI checks to run *on* the bot PR, use a GitHub App token or a fine-grained PAT (`contents` and `pull-requests` write) instead of `GITHUB_TOKEN` [S1]. Otherwise, step 6 above is the only gate.

**History-folder rules:**
- Archive only when the generated output differs.
- Archive the **previous** `proto/` tree as it was on `main`, never the new one.
- Archived folders are immutable: nothing is edited or deleted automatically.
- They are excluded from buf lint and breaking (`buf.yaml` excludes `history/`) and from the golden test.
- Git history already preserves every version, so `history/` is a convenience for readers browsing on GitHub. A lighter alternative is git tags plus release notes.

## 7. Getting the FOM XML into the repo, and the license question

`reference-docs/` is git-ignored, so CI needs another source. The licensing is layered (this is not legal advice):

- **The SISO notice inside every FOM file.** The files carry "Copyright © 2020 by the Simulation Interoperability Standards Organization, Inc. All rights reserved", with two grants:
  - *Schema and API:* "a general, royalty-free license to copy, distribute, display, and make derivative works from this material, for all purposes", provided the attribution "Reprinted with permission from SISO Inc." is included.
  - *Documentation:* the same grant, but **for noncommercial purposes only**.
- **The TrickHLA repository** is under the **NASA Open Source Agreement 1.3** [S18]. GitHub's API reports its license as `NOASSERTION`. NOSA §3A requires redistribution "under this Agreement" with a copy of it included, §3B requires a NASA copyright notice, and §3C requires a change log for modifications. It is unclear whether NOSA governs the SISO-copyrighted FOM files at all, or only NASA's code.
- **Open points:**
  - (a) Is `<semantics>` text "Schema" or "Documentation" under SISO's terms? Our generated `.proto` copies it verbatim into comments.
  - (b) Can generated files containing that text sit under this repo's MIT license?

**Options [D1]:**
- **A. Do not vendor (recommended until clarified).** `fom/SOURCE.json` pins the TrickHLA commit (FOM files currently last changed in `1677fd0`, 2025-12-02; `datatypes.xml` at `ed05f1b`) and the sha256 of each file. CI downloads them at run time. The trigger becomes "`fom/SOURCE.json` changed".
- **B. Vendor into `fom/`** with `NOTICE` (SISO attribution), `LICENSE-NOSA-1.3.txt`, the provenance file and a change log. Do this only after SISO and/or NASA confirm.

Either way, generated files carry the SISO attribution line, and `README.md` should say they are derived works. In either case, ask the SpaceFOM PDG which source they consider authoritative (TrickHLA or SISO's own distribution).

## 8. Phased tasks (rough effort)

| Phase | Work | Effort |
|---|---|---|
| 0 | Decisions D1–D8, `fom/SOURCE.json`, repo setting for Actions PRs | 0.5 day |
| 1 | Parser and model, mapping and emitter for datatypes and environment; golden test passes | 1.5–2 days |
| 2 | Entity (inheritance), management (enums, zero value), interactions, lock-file numbering with reserved handling | 1.5 days |
| 3 | Validation: protoc via grpcio-tools, idempotence, buf lint and breaking config | 0.5–1 day |
| 4 | Workflow: triggers, history archive, create-pull-request, PR body summary; dry run on a branch | 1 day |
| 5 | Docs: README layout, overview mapping additions (zero value, inheritance, lock file) | 0.5 day |

## 9. Decisions for you

- **D1** FOM source: fetch a pinned upstream at CI time (A), or vendor into `fom/` (B) after asking SISO/NASA?
- **D2** One `.proto` per FOM module, or a single file? Package `siso.spacefom.v1`?
- **D3** Scope: datatypes, environment and entity only, or also management? Exclude TrickHLA's `management2.xml`?
- **D4** Enum names: keep the FOM names (`EXEC_MODE_*`) and relax buf lint, or rename to buf style? What should the synthetic zero value for `MTRMode` be called?
- **D5** Emit interaction classes (`ModeTransitionRequest`)?
- **D6** Renames: always a new number (safe), or allow a reviewer-curated `renames` map?
- **D7** Add a scheduled upstream-change check?
- **D8** Is `GITHUB_TOKEN` enough (checks run only inside the generator job), or set up a GitHub App token so CI runs on the bot PR?

## Sources

Fetched or checked on 2026-11-17.

- [S1] peter-evans/create-pull-request README (usage `@v8`, permissions, repo setting, GITHUB_TOKEN caveat, no-diff behaviour, inputs and outputs): https://github.com/peter-evans/create-pull-request
- [S2] GitHub Docs, Automatic token authentication (`permissions` key): https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication
- [S3] GitHub Docs, Workflow syntax (`paths`, `concurrency`, `workflow_dispatch` inputs): https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
- [S4] GitHub Docs, Triggering a workflow (GITHUB_TOKEN events do not create runs, exceptions): https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
- [S5] Same caveat restated in [S1].
- [S6] bufbuild/buf-action README: https://github.com/bufbuild/buf-action
- [S7] Buf docs, GitHub Action parameters (`setup_only`, `breaking_against`, token only for push): https://buf.build/docs/bsr/ci-cd/github-actions/
- [S8] GitHub Docs, Managing GitHub Actions settings for a repository ("Allow GitHub Actions to create and approve pull requests", default off for personal repos): https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- [S9] Protobuf proto3 language guide (enum zero value, field number range, 19000–19999, never reuse, `reserved`, `optional` presence): https://protobuf.dev/programming-guides/proto3/
- [S10] Protobuf style guide (enum value prefixes, `_UNSPECIFIED`, sibling-enum clashes): https://protobuf.dev/programming-guides/style/
- [S11] Buf breaking rules and categories (`FILE` default, `WIRE`): https://buf.build/docs/breaking/rules/
- [S12] Buf inputs reference (`.git#branch=main,subdir=proto`): https://buf.build/docs/reference/inputs/
- [S13] Buf lint rules (`STANDARD`, `ENUM_VALUE_PREFIX`, `ENUM_ZERO_VALUE_SUFFIX`, `PACKAGE_DIRECTORY_MATCH`): https://buf.build/docs/lint/rules/
- [S14] Python `xml.etree.ElementTree` docs (namespaces, document order, security note): https://docs.python.org/3/library/xml.etree.elementtree.html
- [S15] grpcio-tools on PyPI (1.85.1, `python -m grpc_tools.protoc`): https://pypi.org/project/grpcio-tools/
- [S16] protocolbuffers/protobuf releases (latest v36.2): https://github.com/protocolbuffers/protobuf/releases
- [S17] Latest release tags via the GitHub API: create-pull-request v8.1.3, buf-action v1.7.0, checkout v7.0.1, setup-python v7.1.0. For example: https://api.github.com/repos/peter-evans/create-pull-request/releases/latest
- [S18] TrickHLA license, NASA Open Source Agreement 1.3: https://github.com/nasa/TrickHLA/blob/master/LICENSE.txt. FOM files: https://github.com/nasa/TrickHLA/tree/master/FOMs/SpaceFOM
- Local checks: `protoc` 36.2 (`--help` flags, enum-zero error, example compiles); FOM XML files (SISO copyright and license text in `<modelIdentification><other>`).

**Unverified:**
- Whether NOSA 1.3 or SISO's notice governs redistribution of the FOM files (legal question).
- Whether buf `lint` `except`/`ignore` configuration exists as described; I did not fetch the buf.yaml config reference.
- Exact wording of `buf breaking` behaviour on `reserved` additions.
