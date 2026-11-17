# Testing guide

How to check that everything works, step by step. Part 1 runs on your computer. Part 2 and Part 3 happen in the GitHub website and need write access to the repository. Do them in order the first time.

## Contents

- [Part 1: test the generator on your computer](#part-1-test-the-generator-on-your-computer)
- [Part 2: quick check of the automation on GitHub](#part-2-quick-check-of-the-automation-on-github)
- [Part 3: full test, with the bot opening pull requests](#part-3-full-test-with-the-bot-opening-pull-requests)
- [Optional: the six languages on your computer](#optional-the-six-languages-on-your-computer)

## Part 1: test the generator on your computer

You need [conda](https://docs.conda.io) and a copy of the repository. Open a terminal.

1. Go to the repository folder:
   ```sh
   cd /path/to/spacefom2-protobuf
   ```
2. Create a conda environment named `spacefom2` with Python 3.11. You only do this once:
   ```sh
   conda create -n spacefom2 python=3.11 -y
   ```
3. Activate it. Do this every time you open a new terminal:
   ```sh
   conda activate spacefom2
   ```
4. Install what the generator needs:
   ```sh
   pip install -r generator/requirements.txt
   ```
   `requirements.txt` is a lock file with hashes. To change a dependency, edit `generator/requirements.in` (or `samples/python/requirements.in`) and recompile with `pip-compile --generate-hashes`.
5. Tell Python where the generator code is:
   ```sh
   export PYTHONPATH=generator
   ```
6. Download the SpaceFOM FOM files. The command checks each file against the sha256 pinned in `fom/SOURCE.json`:
   ```sh
   python -m spacefom_proto fetch --dest build/fom
   ```
   You should see the paths of four files under `build/fom/`. An error here means a file did not match its sha256.
7. Check that the committed `.proto` files match what the generator produces:
   ```sh
   python -m spacefom_proto generate --fom-dir build/fom --check
   ```
   You should see `Generated files are up to date.`
8. Run all the tests:
   ```sh
   SPACEFOM_FOM_DIR=build/fom python -m pytest -q generator/tests tools
   ```
   The last line should say `114 passed`.

If all three checks look like this, the generator works on your computer.

## Part 2: quick check of the automation on GitHub

The repository has two workflows that do the work. **generate-proto** turns the FOM XML into the `.proto` schema. **generate-samples** turns the schema into code for six languages and tests it. This part starts each one by hand to check that it runs and passes. Nothing changes and no pull request is opened.

### Check 1: generate-proto (about 30 seconds)

1. Open the repository on GitHub and click the **Actions** tab at the top.
2. In the left sidebar, click **generate-proto**.
3. Click the **Run workflow** button above the list of runs.
4. In the form that opens, leave the branch on `main` and tick **dry_run**.
5. Click the green **Run workflow** button in the form.
6. After a few seconds a new run appears at the top of the list. When it finishes, click its name.
7. A green tick means it passed. Scroll down to the summary: it says `Dry run: true`.

### Check 2: generate-samples (about 2 minutes)

1. Still in the **Actions** tab, click **generate-samples** in the left sidebar.
2. Click **Run workflow**, leave the branch on `main` and tick **dry_run**.
3. Click the green **Run workflow** button in the form.
4. When the new run finishes, click its name. It shows one job per language (cpp, csharp, go, java, python, typescript); all of them should have a green tick.
5. Scroll down to the summary: it says `Generated sample code and data are unchanged.`

These steps follow [GitHub Docs: manually running a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

### When to tick dry_run, and when not to

A manual run opens a pull request only on `main`, with **dry_run** clear, and only when the generated output changed (the [trigger table](../../README.md#triggering-the-generation-in-ci) has the rules for every trigger). On an up-to-date `main` nothing changes, so the box makes no difference. It matters when `main` is behind its inputs, for example after an input change was merged but its bot pull request was never opened.

- **Tick it** when you only want to look: the summary reports what would change, and nothing is opened or updated. This is also the safe choice for the checks above.
- **Leave it clear** when you want the bot to act: an automatic run failed or got stuck after you merged a change, or a bot pull request was closed without being merged. The run then regenerates and opens (or updates) the pull request.

You don't need either for the normal flow in Part 3: merging your change starts everything by itself.

## Part 3: full test, with the bot opening pull requests

This is the real flow. You change an input, and the automation regenerates everything through two pull requests that a bot opens. The test bumps the generator version: it changes the first line of every generated file and nothing else, so it is safe. It leaves the repository on a new generator version, which is fine.

The same steps work for a real FOM update; in step 2 you would edit `fom/SOURCE.json` (the upstream commit and the sha256 of each file) instead.

### A. Make the change

1. On GitHub, click the **Code** tab, then open `generator`, `spacefom_proto` and `__init__.py`.
2. Click the pencil icon (**Edit file**) at the top right of the file ([GitHub Docs: editing files](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)).
3. Change the version number on the line `__version__ = "0.1.1"` to the next one, for example `"0.1.2"`. Check the current value first; it may already be higher.
4. Click **Commit changes...**. In the dialog, choose to create a new branch for this commit, then click **Propose changes**.
5. On the next page, click **Create pull request**.

### B. Check and merge your pull request

6. Wait for the checks at the bottom of the pull request to finish (about a minute). They should all pass.
7. Optional: click the **generate-proto** check, then **Summary**. It says the generated output "will be regenerated by the bot after merge". That is expected: you changed an input, and the bot does the regeneration after the merge.
8. Click **Merge pull request**, then **Confirm merge** ([GitHub Docs: merging a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request)).

### C. First bot pull request: the schema

9. Click the **Pull requests** tab. Within a minute or two a new pull request appears, **Regenerate SpaceFOM .proto files**, opened by `github-actions[bot]`. If it is not there yet, wait and refresh. You can follow progress in the **Actions** tab.
10. Open it and click **Files changed**. You should see:
    - the four files in `proto/siso/spacefom/v1/`, each with only the version line changed;
    - a new folder under `history/` holding the previous version, plus a `MANIFEST.json`.
11. Go back to the **Conversation** tab. Its checks show "awaiting approval", because a bot opened the pull request ([GitHub changelog, 11 June 2026](https://github.blog/changelog/2026-06-11-bot-created-pull-requests-can-run-workflows-if-approved/)). Click **Approve workflows to run** ([GitHub Docs: approving workflow runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks)).
12. Wait for the checks to pass (about two minutes, because the six languages are built), then click **Merge pull request** and **Confirm merge**.

### D. Second bot pull request: the samples

13. Merging the schema starts the samples workflow. In the **Pull requests** tab, a second pull request appears after a few minutes: **Regenerate sample bindings and data**, also from `github-actions[bot]`.
14. Open it and click **Files changed**. Only the Go and TypeScript files change, one line each, because those are the languages whose generated code repeats the version line.
15. Click **Approve workflows to run**, wait for the checks to pass, then click **Merge pull request** and **Confirm merge**.

### E. Check that it finished

16. Open the **Actions** tab. The newest **generate-samples** run, started by your last merge, should be green. Open it: its summary says `Generated sample code and data are unchanged.`
17. The **Pull requests** tab shows no new bot pull request.

If both are true, the full flow works. [This run](https://github.com/gsantopaolo/spacefom2-protobuf/actions/runs/44095824846) shows what the final step looked like in the end-to-end test of 17 November 2026.

## Optional: the six languages on your computer

`sh samples/test-all.sh` regenerates the bindings and builds and tests C++, Python, Java, C#, TypeScript and Go locally. It needs extra toolchains (protoc, buf, Go, Node, Java with Maven, .NET and CMake); [`samples/README.md`](../../samples/README.md) lists the exact versions. CI already runs all six on every change, so you can skip this.
