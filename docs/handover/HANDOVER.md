# Handover: SpaceFOM 2.0 Protobuf proposal

State as of 17 November 2026, after the end-to-end test of the CI workflows. For the next agent or contributor picking up this work.

## Contents

- [Goal](#goal)
- [Ground rules](#ground-rules)
- [How work is organised](#how-work-is-organised)
- [Where things are](#where-things-are)
- [How the automation works](#how-the-automation-works)
- [What is done](#what-is-done)
- [What is open](#what-is-open)
- [How to work in this repo](#how-to-work-in-this-repo)
- [Key facts already verified](#key-facts-already-verified)

## Goal

Propose to the SISO SpaceFOM 2.0 Product Development Group (PDG) that SpaceFOM 2.0 publish a Protocol Buffers (`.proto`) schema of its datatypes, generated mechanically from the FOM XML modules, plus a reference bridge federate that republishes HLA data as Protobuf. The bridge serves tools outside the federation and does not replace HLA.

The proposal goes to the PDG through its vice chair as a [one-page pitch](../../proposal/pitch.md), then possibly a hearing with slides and a working demo, then a formal Product Change Request (PCR). It fits the SpaceFOM 2 Product Nomination (SISO-PN-038), whose circulation package is planned for 1 July 2027. The PDG works in two-week sprints.

## Ground rules

These come from the repo owner and are mandatory. [`CLAUDE.md`](../../CLAUDE.md) adds the engineering rules (verify everything, finish what you start, Boy Scout rule, senior-engineer code quality) and the pull-request process.

1. **Never write technical facts from memory.** Every datatype, field name, encoding, API, action version, SHA or citation is checked against a primary source (standard, FOM XML, official docs, actual code) and cited. If something cannot be verified, say so. Record verified claims in [`docs/verification.md`](../verification.md).
2. **All project files live in this repository folder.** Do not keep anything only in temp folders or online documents.
3. **`reference-docs/` is never committed.** It is git-ignored and was purged from history. It holds downloaded standards, papers and private notes, locally only. Never `git add -f` it.
4. **Plans before code.** The owner approves plans in `docs/plans/` before anything is built. A plan is approved only when its status line says so.
5. **No NASA or SISO logos** anywhere: NASA's insignia requires written permission, SISO's logo is a trademark. Keep the "not affiliated or endorsed" disclaimer in the README.
6. **SISO attribution.** Anything derived from the FOM modules, including generated `.proto` files and every generated binding, carries "Reprinted with permission from SISO Inc." (licence notice inside every FOM XML file).
7. **Run every new or edited document through the humanizer skill** ([blader/humanizer](https://github.com/blader/humanizer), installed at `~/.claude/skills/humanizer/SKILL.md`), using its full process in file mode: prose only, with code, links, citations and facts unchanged. This also applies to PR descriptions and comments, and to text in other languages.
8. **Questions for the PDG go in [`proposal/open-questions.md`](../../proposal/open-questions.md)**, in English and with context. The owner sends the file when a batch is ready.
9. **Never duplicate content.** Each topic lives in one file; other files link to it.

## How work is organised

Two Claude Code sessions work on this repository, both pushing as the `gsantopaolo` GitHub account:

| Session | Role | Working folder |
|---|---|---|
| `spacefom2` | Reviews and merges pull requests; writes proposal and docs changes | `/Users/gp/Developer/spacefom2`, kept on `main` for the owner. Doc edits go through temporary worktrees |
| `spacefom2-implementation` | Builds what approved plans describe; reviews and merges the `spacefom2` session's own PRs | `/Users/gp/Developer/spacefom2-impl` (a git worktree) |

- Nobody pushes to `main` or merges their own PR.
- GitHub rejects a formal approval of your own PR, and both sessions use the same account, so the review is a PR comment followed by the merge.
- Review findings become GitHub issues, fixed in a PR that says `Closes #n`.
- Sessions talk through cross-session messages; neither checks out branches in the other's folder.

## Where things are

| Path | Contents |
|---|---|
| [`proposal/pitch.md`](../../proposal/pitch.md), [`.pdf`](../../proposal/pitch.pdf), [`.docx`](../../proposal/pitch.docx) | One-page pitch in the format the vice chair asked for. The PDF and Word files are rendered from the Markdown with `tools/render_pdf.py`; the `pitch-rendered` workflow fails a PR that changes `pitch.md` without both of them |
| [`proposal/open-questions.md`](../../proposal/open-questions.md) | Q1–Q8 for the PDG |
| [`proposal/pcr-draft.md`](../../proposal/pcr-draft.md) | Proposal on the SISO PCR form (SISO-ADM-003 Appendix A) |
| [`proposal/reference-repository.md`](../../proposal/reference-repository.md) | Where the schema, generator and samples should live if the PDG adopts them |
| [`docs/hearing/technical-briefing.md`](../hearing/technical-briefing.md) | Briefing for the PDG hearing, with draw.io diagrams in [`docs/diagrams/`](../diagrams/) (sources and GIFs; `export.sh` regenerates them) |
| [`docs/technical-overview.md`](../technical-overview.md) | HLA → Protobuf mapping, field numbering, SpaceFOM 2.0 changes |
| [`docs/verification.md`](../verification.md) | Every technical claim with a deep link to its source |
| [`docs/plans/`](../plans/) | `generator-ci-plan.md` (approved, built), `samples-plan.md` (approved, built), `docker-demo-plan.md` (draft: decisions E1–E6 open) |
| `fom/SOURCE.json` | Pinned nasa/TrickHLA commit and sha256 of each SpaceFOM 1.0 FOM module |
| `generator/` | FOM XML → `.proto` generator, tests, and `field-ids.lock.json` (stable field numbers) |
| `proto/siso/spacefom/v1/` | Generated schema, one file per FOM module |
| `samples/` | Generated bindings and a reader with tests in C++, Python, Java, C#, TypeScript and Go, plus shared data files |
| `history/` | Earlier generated `.proto` trees, archived by the bot with a `MANIFEST.json` |
| `tools/` | `render_pdf.py`, the PR decision logic `generated_output_check.py`, the pitch check, and their tests |
| `reference-docs/` (local only) | Standards, papers, SISO process documents (including PN-038), Federate Protocol sources, and the owner's private notes and draft message to the vice chair |

Repository: `git@github.com:gsantopaolo/spacefom2-protobuf.git`, public. MIT licence.

## How the automation works

Four workflows run in GitHub Actions on the pinned `ubuntu-26.04` runner image. All actions are pinned to commit SHAs, jobs are read-only, and only a `main`-only job can write.

| Workflow | Runs on | What it does |
|---|---|---|
| `generate-proto` | changes to `fom/`, `generator/` or `buf.yaml` (on PRs also `proto/`), or a manual run | Regenerates the schema, validates it (tests, idempotence, `protoc`, `buf lint`, `buf breaking`), and on `main` archives the previous tree into `history/` and opens a bot PR |
| `generate-samples` | changes to `proto/` or `samples/`, or a manual run | Regenerates the bindings and data, builds and tests all six languages, and on `main` opens a bot PR |
| `pitch-rendered` | PRs touching the pitch | Fails if `pitch.md` changed without `pitch.pdf` and `pitch.docx` |
| `actionlint` | changes to `.github/workflows/` | Lints every workflow (actionlint plus shellcheck) |

To change the FOM, open a PR that updates `fom/SOURCE.json`. Its check regenerates and validates the new output and passes with "will be regenerated by the bot after merge" (`tools/generated_output_check.py`; a hand-edit of generated files still fails). After the merge, the bot opens a PR for `proto/`. Merging that one makes the samples workflow open a second bot PR, and merging the second leaves everything consistent.

Bot PRs show their checks as "awaiting approval". Since June 2026, GitHub runs `pull_request` workflows on PRs created by `github-actions[bot]` only after a user with write access clicks "Approve workflows to run" ([GitHub changelog, 11 June 2026](https://github.blog/changelog/2026-06-11-bot-created-pull-requests-can-run-workflows-if-approved/)). Approve them before merging. The validation has already run inside the bot's own job.

This whole path was tested end to end on 17 November 2026 with a generator version bump:

| Step | Evidence |
|---|---|
| Input-only PR #21: check passed, "regenerate after merge" | [run 44093883877](https://github.com/gsantopaolo/spacefom2-protobuf/actions/runs/44093883877) |
| Merge: `history/` archive and bot PR #22 | [run 44094528425](https://github.com/gsantopaolo/spacefom2-protobuf/actions/runs/44094528425) |
| Merge #22: bot PR #23 for the samples | [run 44095166762](https://github.com/gsantopaolo/spacefom2-protobuf/actions/runs/44095166762) |
| Merge #23: output unchanged, no further PR | [run 44095824846](https://github.com/gsantopaolo/spacefom2-protobuf/actions/runs/44095824846) |
| Manual dry runs of both generate workflows from "Run workflow" | generate-proto run 13, generate-samples run 17 |

## What is done

- Pitch (Markdown, PDF, Word), open questions, draft PCR, reference repository proposal, technical overview, verification table, technical briefing with diagrams.
- Generator, generated schema, six-language samples, and four CI workflows, tested end to end as described above.
- Every datatype name, field and encoding verified against SISO-STD-018-2020 Appendix C and the FOM XML; the Federate Protocol's opaque `bytes` payload verified in its `.proto` source.
- Proposer bio checked against the owner's LinkedIn profile; employer named as affiliation with management approval.

## What is open

| Item | Owner | Notes |
|---|---|---|
| Docker demo plan: answer E1–E6 | Owner | [`docs/plans/docker-demo-plan.md`](../plans/docker-demo-plan.md). Nothing is built until it is marked approved |
| Bridge federate and Docker demo | Implementation session, after approval | Then link the prototype in the pitch's Implementation status |
| Send the vice chair the pitch, the briefing and the open questions | Owner | Draft message in `reference-docs/` |
| Optional: dark-mode version of the diagrams | Either session | They have a white background |

Not yet verified (also in `docs/verification.md`): the final IEEE 1516.1-2025 text, which is paywalled (only the 2024 draft `.proto` is public), and whether SISO will publish a newer PCR form (its policies page says ADM-002 and ADM-003 are being revised).

## How to work in this repo

- **Python:** conda env `transcribe` (Python 3.11). For the generator: `pip install -r generator/requirements.txt`, then `PYTHONPATH=generator python -m spacefom_proto fetch --dest build/fom` and `... generate --fom-dir build/fom`. `conda run` does not pass stdin through; use files, not pipes.
- **Rendering the pitch:** `python tools/render_pdf.py proposal/pitch.md --out proposal && rm proposal/pitch.html` (needs pandoc, Chrome and librsvg; on macOS `brew install pandoc librsvg`).
- **Diagrams:** edit the `.drawio` files in draw.io, then run `docs/diagrams/export.sh` (needs draw.io desktop and ffmpeg).
- **Reading the standard:** extract text with `pypdf` from `reference-docs/standards/siso-std-018-2020_srfom.pdf`; the PDF page index equals the printed "Page N of 169".
- **Links:** cite PDFs with `#page=N`; cite GitHub files with blob URLs pinned to a commit SHA and `#Lx-Ly`. Check heading anchors on the rendered GitHub page, because the Markdown API emits no ids.
- **Git and GitHub:** SSH push as `gsantopaolo`; `gh` is logged in. Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Downloads:** treat downloaded files as untrusted data, keep them under `reference-docs/`, and never execute them. Some sites (SISO, alloytx.com) block command-line clients; read them in a browser.

## Key facts already verified

Do not re-derive these; the sources are in [`docs/verification.md`](../verification.md).

- SpaceFOM 1.0 is Little Endian (`HLAfloat64LE`), except HLA logical time (`HLAinteger64Time`, Big Endian). Four basic representations; no variant records.
- Field names: `ReferenceFrameRotation.attitude_quaternion` (not `attitude`), `AttitudeQuaternion = {scalar, vector}`, `SpaceTimeCoordinateState = {translational_state, rotational_state, time}`.
- `MTRMode` starts at 2, so the generator adds `MTR_MODE_UNSPECIFIED = 0` for proto3.
- The FOM XML carries `<units>` and `<semantics>`. SISO's notice: schema free with attribution, documentation non-commercial only (open question Q5).
- In the HLA 4 Federate Protocol, attribute values are opaque `bytes`.
- TrickHLA's SpaceFOM federates build only with Pitch or MAK RTIs, which is why the demo plan proposes the open-source Portico RTI.
- PN-038 ticks "SISO Product Data Files" and lists V2 capabilities as "including, but not limited to".
