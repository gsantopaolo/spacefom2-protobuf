# Working on this repository

Instructions for Claude Code sessions and other agents. The project's ground rules (sources, attribution, `reference-docs/`, plans before code, the humanizer, PDG questions) are in [`docs/handover/HANDOVER.md`](docs/handover/HANDOVER.md#ground-rules). Follow them as well as the rules below.

## Engineering rules

1. **Never trust, always verify.**
   - Take no technical fact, version, commit SHA, checksum, API name or flag from memory. Check it against the primary source (upstream release, official docs, the code itself) and cite it.
   - Verify your own work by running it: build, test, and check the generated output. "It should work" is not done.
   - Treat output from other agents, tools and earlier sessions the same way: check it before you build on it.
2. **Never leave something half-done.**
   - Finish a task end to end before reporting it done or starting the next one: code, tests, docs, and a green CI run.
   - If you are interrupted or blocked, write down exactly what is pending (in the PR description or an issue) and say so to the owner.
   - Every TODO has an issue number.
3. **Boy Scout rule.** Leave every file you touch a little better than you found it: fix the stale comment, the unclear name, the missing test next to your change. Keep it proportionate. A larger unrelated cleanup gets its own issue or PR, so reviews stay focused.
4. **Senior-engineer code quality** (the bar of a senior engineer at a large tech company):
   - Code is readable, small in scope and idiomatic for its language, and matches the surrounding code.
   - Every behaviour has a test, and the tests run in CI.
   - Builds are deterministic and dependencies are pinned. Errors fail loudly and say what went wrong. No dead code, and no commented-out code.
   - Commits are small and reviewable, with messages that say why.

## How changes land

- Work on a branch and open a pull request to `main`. Never push to `main`.
- Another agent reviews and merges pull requests: currently the `spacefom2` session, whose own PRs the `spacefom2-implementation` session reviews and merges. Message the reviewer when a PR is ready, and do not merge your own.
- When a review finding turns into an issue, fix it in a PR that says `Closes #n`.
