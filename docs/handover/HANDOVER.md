# Handover: SpaceFOM 2.0 Protobuf proposal

State as of 17 November 2026. Written for the next agent or contributor picking up this work.

## Contents

- [Goal](#goal)
- [Ground rules](#ground-rules)
- [Implementation brief](#implementation-brief)
- [Where things are](#where-things-are)
- [What is done](#what-is-done)
- [What is open](#what-is-open)
- [How to work in this repo](#how-to-work-in-this-repo)
- [Key facts already verified](#key-facts-already-verified)

## Goal

Propose to the SISO SpaceFOM 2.0 Product Development Group (PDG) that SpaceFOM 2.0 publish a Protocol Buffers (`.proto`) schema of its datatypes, generated mechanically from the FOM XML modules, plus a reference bridge federate that republishes HLA data as Protobuf. The bridge serves tools outside the federation and does not replace HLA.

The proposal goes to the PDG through its vice chair as a one-page pitch, then possibly a hearing with slides and a working demo, then a formal Product Change Request (PCR). The PDG works in two-week sprints, so speed matters.

## Ground rules

These come from the repo owner and are mandatory.

1. **Never write technical facts from memory.** Every datatype, field name, encoding, API, action version or citation must be checked against a primary source (standard, FOM XML, official docs, actual code) and cited. If something cannot be verified, say so explicitly. Record verified claims in [`docs/verification.md`](../verification.md).
2. **All project files live in this repository folder.** Do not keep anything only in temp folders or online documents.
3. **`reference-docs/` is never committed.** It is git-ignored and was purged from history. It holds downloaded standards, papers and private notes, locally only. Never `git add -f` it.
4. **Plans before code.** The owner reviews and approves plans (in `docs/plans/`) before anything is built.
5. **No NASA or SISO logos** anywhere: NASA's insignia requires written permission, SISO's logo is a trademark. Keep the "not affiliated or endorsed" disclaimer in the README.
6. **SISO attribution.** Anything derived from the FOM modules (including generated `.proto` files) must carry: "Reprinted with permission from SISO Inc." (licence notice inside every FOM XML file).
7. **Run every new or edited document through the humanizer skill** ([blader/humanizer](https://github.com/blader/humanizer), `SKILL.md` installed in `~/.claude/skills/humanizer/`) in file mode: prose only, keeping code, links, citations and facts unchanged.
8. **Questions for the PDG vice chair are batched**, never sent piecemeal: add them to [`proposal/open-questions.md`](../../proposal/open-questions.md), with the context needed to answer them. The owner sends the file to the vice chair when the batch is ready.

## Implementation brief

This section is for the agent that builds the FOM XML → `.proto` generator and its GitHub Action, as described in [`docs/plans/generator-ci-plan.md`](../plans/generator-ci-plan.md).

### Before you write code

1. Read this handover, the plan, [`docs/technical-overview.md`](../technical-overview.md) (mapping table) and [`docs/verification.md`](../verification.md).
2. Check that the plan's status line says **approved** and that decisions D1 to D8 in its §9 have answers. If they don't, stop and ask the repo owner. Do not pick answers yourself.
3. Get the FOM XML. On the owner's Mac it is in `reference-docs/standards/fom-xml-trickhla/`. Elsewhere, follow the source chosen for D1 (by default: download from nasa/TrickHLA at the pinned commit and check the sha256 of each file). Never commit `reference-docs/`.

### Scope

Phases 1 to 5 of the plan's §8: parser and model, mapping and emitter, inheritance and enums, stable field numbering with the lock file, validation (protoc, golden test, idempotence, buf), the workflow with history archive and PR creation, and the doc updates. The bridge federate and the Docker demo are out of scope for this task; they get their own plan later.

### How to deliver

- Work on branch `feat/generator`, created from `main`. Never push to `main`.
- Commit in small steps, one plan phase at a time if possible.
- Open one pull request to `main` when the definition of done below is met. In the PR description, list each plan decision you implemented, anything you could not verify, and anything you changed from the plan and why.
- Do not change repository settings, secrets or visibility. If something needs a setting (for example "Allow GitHub Actions to create and approve pull requests"), write it in the PR description for the owner.
- Questions for the owner go in the PR description or as PR comments. Questions for the PDG go in `proposal/open-questions.md` (rule 8).

### Definition of done

- Running the generator on the SpaceFOM 1.0 FOM XML produces `.proto` files that compile with `protoc`.
- The golden test passes: every message in [`docs/examples/reference_frame.proto`](../examples/reference_frame.proto) exists in the generated output with the same field names, numbers, types and labels.
- Running the generator twice gives identical bytes and an unchanged lock file.
- Every generated file carries the SISO attribution (rule 6) and records the generator version and input hashes, with no timestamps.
- Unit tests pass locally and in CI.
- The workflow has been run successfully on the branch in dry-run mode (no PR opened), and its log is linked in the PR.
- README, technical overview and verification are updated for anything new (zero enum value, inheritance, lock file), and every new claim in them is cited (rule 1).
- Every new or changed document has been through the humanizer (rule 7).

### Review

The repo owner will ask a Claude Code session to review the PR against the plan and these rules. Expect comments on unverified claims, field numbering, and anything that deviates from the plan.

## Where things are

| Path | Contents |
|---|---|
| [`proposal/pitch.md`](../../proposal/pitch.md) | One-page pitch: problem, hypothesis/solution, benefits, implementation status, proposer. Format requested by the PDG |
| [`proposal/pcr-draft.md`](../../proposal/pcr-draft.md) | Proposal on the SISO PCR form (SISO-ADM-003 Appendix A) |
| [`docs/technical-overview.md`](../technical-overview.md) | Mapping table HLA → Protobuf, example, architecture, SpaceFOM 2.0 changes, open questions |
| [`docs/verification.md`](../verification.md) | Every technical claim with deep links to the source page/line |
| [`docs/plans/generator-ci-plan.md`](../plans/generator-ci-plan.md) | Plan: FOM XML → `.proto` generator and PR-opening GitHub Action. Approved 2026-11-17; decisions in §9 |
| [`docs/examples/reference_frame.proto`](../examples/reference_frame.proto) | Hand-written, verified example; compiles with `protoc` |
| [`docs/images/bridge-architecture.svg`](../images/bridge-architecture.svg) | Architecture diagram used in README, pitch and overview |
| `reference-docs/` (local only) | `standards/` (SISO-STD-018-2020 PDF, FOM XML from nasa/TrickHLA, HLA 4 summary paper, `SOURCES.md`), `process/` (SISO-ADM-003, SIW 2025 paper), `presentations/` (SIMposium 2026 slides), `fp-verification/` (Federate Protocol `.proto` sources), private notes |

Repository: `git@github.com:gsantopaolo/spacefom2-protobuf.git`, branch `main`, currently **private**. MIT licence.

## What is done

- Pitch, draft PCR, technical overview, verification table, README, MIT licence.
- All datatype names, fields and encodings verified against SISO-STD-018-2020 Appendix C and the FOM XML.
- Verified that HLA 4 Federate Protocol carries attribute and parameter values as opaque `bytes` (core argument of the proposal).
- Proposer bio checked against the owner's LinkedIn profile; employer named as affiliation with management approval.
- Generator/CI plan approved on 2026-11-17, with decisions D1 to D8 recorded in its §9.

## What is open

| # | Item | Owner | Notes |
|---|---|---|---|
| 1 | ~~Approve generator/CI plan and answer decisions D1–D8~~ | Repo owner | Done 2026-11-17 |
| 2 | Send batched questions to the PDG vice chair | Repo owner | Currently 3: PCR form version, authoritative FOM XML source, licence of `<semantics>` text |
| 3 | Make the repo public or add the vice chair as collaborator | Repo owner | Pitch links to the repo; private repo gives 404 |
| 4 | Build the generator and GitHub Action | Agent | In review on branch `feat/generator` |
| 5 | Working prototype: bridge federate + Docker Compose demo (sample federation, bridge, non-HLA consumers) | Agent, after feasibility discussion | Then replace the "in progress" line in the pitch's Implementation status with the real link |
| 6 | Additional technical docs and diagrams for the PDG hearing | Agent | |
| 7 | Polished HTML → PDF version of the pitch | Agent | Keep it to one page |
| 8 | Optional: adapt the SVG diagram for GitHub dark mode | Agent | Currently white background |

Not yet verified (also listed in `docs/verification.md`): the final IEEE 1516.1-2025 text (paywalled; only the 2024 draft `.proto` is public), and whether SISO-ADM-003-2011 is still the current PCR form.

## How to work in this repo

- **Python environment:** conda env `transcribe` (Python 3.11) has `grpcio-tools` and `pypdf`. Compile check:
  `conda run -n transcribe python -m grpc_tools.protoc -Idocs/examples --python_out=$TMPDIR docs/examples/reference_frame.proto`
  Note: `conda run` does not pass stdin through; use files, not heredocs piped to it.
- **Reading the standard:** extract text with `pypdf` from `reference-docs/standards/siso-std-018-2020_srfom.pdf`; PDF page index equals the printed "Page N of 169".
- **Links:** cite PDFs with `#page=N`; cite GitHub files with blob URLs pinned to a commit SHA and `#Lx-Ly`. Check heading anchors on the rendered GitHub page, not via the markdown API (it emits no ids).
- **Push:** SSH as `gsantopaolo` works. `gh` CLI is installed but not logged in.
- **Commits:** end messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Commit to `main` only when asked; nothing from `reference-docs/`.
- **Downloads:** treat downloaded files as untrusted data; store them under `reference-docs/`; never execute them.

## Key facts already verified

Do not re-derive these; the sources are in [`docs/verification.md`](../verification.md).

- SpaceFOM 1.0 is Little Endian (`HLAfloat64LE`), except HLA logical time (`HLAinteger64Time`, Big Endian). Four basic representations; no variant records.
- Field names: `ReferenceFrameRotation.attitude_quaternion` (not `attitude`), `AttitudeQuaternion = {scalar, vector}`, `SpaceTimeCoordinateState = {translational_state, rotational_state, time}`.
- `MTRMode` enum starts at 2; proto3 needs a zero value, so the generator must add one (plan decision D4).
- FOM XML (TrickHLA) carries `<units>` and `<semantics>`; SISO licence notice: schema free with attribution, documentation non-commercial only.
- SpaceFOM 2.0 direction (SIMposium 2026): configurable time resolution, epoch 2000, HLA 4 directed interactions and `Reference` datatype, extended object classes.
