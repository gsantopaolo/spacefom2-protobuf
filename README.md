<div align="center">

# SpaceFOM ⇄ Protobuf

**A Protocol Buffers schema for the SISO SpaceFOM datatypes, generated from the FOM modules,<br>so cloud, streaming, robotics and MBSE tools can read space-simulation data without speaking HLA.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-proposal-orange.svg)](proposal/pitch.md)
[![Target](https://img.shields.io/badge/target-SpaceFOM%202.0-6f42c1.svg)](https://ntrs.nasa.gov/citations/20260008222)
[![Base](https://img.shields.io/badge/based%20on-SISO--STD--018--2020-555.svg)](https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf)

<img src="docs/images/bridge-architecture.svg" alt="HLA stays inside the federation; Protobuf carries SpaceFOM data out" width="760">

</div>

## What this is

[SpaceFOM](https://cdn.ymaws.com/www.sisostandards.org/resource/resmgr/standards_products/siso-std-018-2020_srfom.pdf) (SISO-STD-018-2020) is the SISO standard for interoperable, HLA-based space-mission simulation, now being evolved into **SpaceFOM 2.0** by the SISO Product Development Group.

Today, SpaceFOM data can only be read by software that speaks HLA. This project proposes that SpaceFOM 2.0 also publish a `.proto` schema of its datatypes, generated mechanically from the FOM XML, plus a reference bridge federate that republishes HLA updates as Protobuf on Kafka or gRPC.

Federation roles, synchronization and time management stay in HLA; the schema is for tools outside the federation.

## Read the proposal

| Document | What it is |
|---|---|
| **[One-page pitch](proposal/pitch.md)** ([PDF](proposal/pitch.pdf), [Word](proposal/pitch.docx)) | Problem, solution, expected benefits, proposer: the summary for the SpaceFOM 2.0 PDG |
| [Draft PCR](proposal/pcr-draft.md) | The proposal on the SISO Problem/Change Request form (SISO-ADM-003, Appendix A) |
| [Technical briefing for the hearing](docs/hearing/technical-briefing.md) | How the proposal works, with diagrams: architecture, generator pipeline, the path of one update, field numbering |
| [Open questions for the PDG](proposal/open-questions.md) | Every decision the proposal needs from the PDG, with context |
| [Reference repository proposal](proposal/reference-repository.md) | Where the schema, generator and multi-language samples should live if the PDG adopts them: options and the decisions needed |
| [Technical overview](docs/technical-overview.md) | HLA-to-Protobuf mapping, example `.proto`, architecture |
| [Verification](docs/verification.md) | Every technical claim, with the clause of the standard it was checked against |
| [Generator and CI plan](docs/plans/generator-ci-plan.md) | Approved plan for the FOM XML → `.proto` generator and the GitHub Action that opens update PRs |
| [Generated schema](proto/siso/spacefom/v1/) | The `.proto` files generated from the SpaceFOM 1.0 FOM modules, package `siso.spacefom.v1` |
| [Samples](samples/README.md) | Generated code, a reader program and tests in C++, Python, Java, C#, TypeScript and Go, and the two-workflow pipeline that keeps them in step with the FOM |

## Example

`ReferenceFrame`, as defined in SISO-STD-018-2020 (Tables C-4 to C-7, C-13), rendered as Protobuf. Full file: [docs/examples/reference_frame.proto](docs/examples/reference_frame.proto).

```protobuf
message SpaceTimeCoordinateState {
  ReferenceFrameTranslation translational_state = 1;
  ReferenceFrameRotation rotational_state = 2;
  double time = 3;  // Time: simulated physical time (TT), s
}

message ReferenceFrame {
  optional string name = 1;
  optional string parent_name = 2;  // empty for the root frame
  optional SpaceTimeCoordinateState state = 3;
}
```

## Roadmap

- [x] Proposal, draft PCR and verified example schema
- [x] FOM XML → `.proto` generator, with CI
- [x] Generated code, samples and tests in six languages
- [ ] Bridge federate: HLA updates → Protobuf → Kafka / gRPC
- [ ] Docker Compose demo: sample federation, bridge and non-HLA consumers
- [ ] Technical documentation and diagrams for the PDG hearing (first version: [technical briefing](docs/hearing/technical-briefing.md))

## Generating the schema

The generator is plain Python 3.11 and needs no XML library beyond the standard one. It downloads the four SISO FOM modules from the [nasa/TrickHLA][trickhla] commit pinned in [`fom/SOURCE.json`](fom/SOURCE.json), checks their sha256, and writes `proto/`.

To test it locally, run these from the repository root in a dedicated conda environment:

```sh
conda create -n spacefom2 python=3.11 -y
conda activate spacefom2
pip install -r generator/requirements.txt
export PYTHONPATH=generator
python -m spacefom_proto fetch --dest build/fom
python -m spacefom_proto generate --fom-dir build/fom --check
SPACEFOM_FOM_DIR=build/fom python -m pytest -q generator/tests tools
```

`fetch` prints the paths of the four FOM files under `build/fom/` and fails if a sha256 does not match. `generate --check` writes nothing; it prints "Generated files are up to date." or fails if the committed files are out of date. Drop `--check` to rewrite `proto/`. The tests should end with `42 passed`: the generator's unit, golden and idempotence tests plus the tests of the CI check scripts in `tools/`.

`--no-semantics` leaves the FOM's `<semantics>` text out of the comments, and `--no-interactions` leaves out `ModeTransitionRequest`. Field numbers are kept stable by [`generator/field-ids.lock.json`](generator/field-ids.lock.json) (see [Field numbers](docs/technical-overview.md#field-numbers)).

To build and test the samples in all six languages, run `sh samples/test-all.sh`; it needs the extra toolchains listed in [`samples/README.md`](samples/README.md). To test the automation on GitHub, follow [Triggering the generation in CI](#triggering-the-generation-in-ci).

### Triggering the generation in CI

The [`generate-proto`](.github/workflows/generate-proto.yml) workflow runs the same steps on GitHub. What it does depends on how it starts:

| Trigger | What happens |
|---|---|
| Push to `main` that changes `fom/`, `generator/`, `buf.yaml`, `tools/generated_output_check.py` or the workflow | Regenerates, runs the tests, `buf lint` and `buf breaking`. If the output changed, it copies the previous tree into `history/` and opens (or updates) a pull request from `generator/proto-update` |
| Push to any other branch, same paths | The same run as a dry run: it reports what would change and never opens a pull request |
| Pull request | Regenerates and runs every check on the fresh output, but opens nothing. A PR that changes only the inputs (`fom/`, `generator/`, `buf.yaml`) passes with a stale `proto/`, because the bot regenerates it after the merge. A PR that edits `proto/` or the lock file by hand fails if they don't match what the generator produces |
| Manual run | Same as a push to the branch you pick; tick `dry_run` to skip the pull request on `main` |

Everything below is done in the GitHub web UI and needs write access to the repository.

#### Running a workflow by hand

The steps follow [GitHub Docs: manually running a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

1. Open the **Actions** tab and click **generate-proto** (or **generate-samples**) in the left sidebar.
2. Click **Run workflow** above the list of runs and pick `main` in the **Branch** dropdown.
3. Tick `dry_run` to get a report only. Leave it clear and the workflow opens a pull request if the output changed.
4. Click **Run workflow** in the form.
5. Click the run's name in the list to open its summary page ([GitHub Docs: viewing workflow run history](https://docs.github.com/en/actions/how-tos/monitor-workflows/view-workflow-run-history)). For `generate-proto` the summary says whether it was a dry run and lists any field-number changes.

#### Moving to a newer FOM

A FOM change reaches the samples through three pull requests:

1. Open [`fom/SOURCE.json`](fom/SOURCE.json) on `main` and click the pencil icon (**Edit file**). Change `commit` to the new upstream commit and update the `sha256` of each file that changed ([GitHub Docs: editing files](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)).
2. Click **Commit changes...**, choose to create a new branch for the commit, click **Propose changes**, then **Create pull request**. You don't need to regenerate `proto/`: CI regenerates it, runs every check on the result, and the `generate-proto` run summary says the output "will be regenerated by the bot after merge".
3. When the checks pass, click **Merge pull request**, then **Confirm merge** ([GitHub Docs: merging a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request)). `generate-proto` then runs on `main`, copies the previous tree into `history/`, and opens the pull request "Regenerate SpaceFOM .proto files" from `generator/proto-update`.
4. Find that pull request in the **Pull requests** tab. Its validation already ran inside the generating run, but its own checks wait as "awaiting approval" because a bot opened it ([GitHub changelog, 11 June 2026](https://github.blog/changelog/2026-06-11-bot-created-pull-requests-can-run-workflows-if-approved/)). Review **Files changed**, click **Approve workflows to run** ([GitHub Docs: approving workflow runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks)), wait for the checks to pass, then click **Merge pull request** and **Confirm merge**.
5. That merge changes `proto/`, which starts [`generate-samples`](.github/workflows/generate-samples.yml) on `main`. It regenerates the code for six languages and the sample data, builds and tests every language, and opens "Regenerate sample bindings and data" from `generator/samples-update`. Approve and merge it as in step 4.

The last merge starts `generate-samples` once more. It is done when that run's summary says "Generated sample code and data are unchanged." and no new pull request appears, as in [this run](https://github.com/gsantopaolo/spacefom2-protobuf/actions/runs/44095824846) from the end-to-end test.

You can also commit the regenerated output in the same pull request as the FOM change, but then it has to match the generator exactly, or the check fails. [`samples/README.md`](samples/README.md) shows the same flow as a diagram.

## Repository layout

```
proposal/    one-page pitch, draft PCR, open questions, reference repository proposal
tools/       render_pdf.py (Markdown to HTML, PDF and Word; needs pandoc, Chrome, librsvg) and the CI check scripts with their tests
.github/     the four CI workflows: generate-proto, generate-samples, pitch-rendered, actionlint
docs/        technical overview, verification, plans, diagrams, example .proto
fom/         SOURCE.json: pinned upstream commit and sha256 of each FOM module
generator/   the FOM XML -> .proto generator, its tests and the field-number lock file
proto/       generated .proto files (do not edit by hand)
history/     earlier generated trees, added by CI when the output changes
samples/     generated code and tests in six languages (see samples/README.md)
```

[trickhla]: https://github.com/nasa/TrickHLA/tree/master/FOMs/SpaceFOM

## Disclaimer

Independent proposal by [Gian Paolo Santopaolo](https://github.com/gsantopaolo). Not affiliated with, endorsed by, or an official product of SISO, NASA or any other organization. SpaceFOM and SISO-STD-018-2020 are © SISO; this repository does not reproduce the standard and refers to it by clause. The `.proto` definitions are derived works of the SpaceFOM FOM modules, and the generated files copy the modules' `<semantics>` text into comments: Reprinted with permission from SISO Inc. Whether that text falls under SISO's "Schema" or "Documentation" licence is an [open question for the PDG](proposal/open-questions.md#sources-and-licence).

Prepared with Claude (Anthropic) as a research and drafting aid; every technical fact was checked against the primary sources listed in [verification](docs/verification.md).

## License

[MIT](LICENSE) © 2026 Gian Paolo Santopaolo
