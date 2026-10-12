# SC4 dry run — result (orchestrator step O2, 2026-10-12)

**Verdict: SC4 met.** A fresh agent, seeing only the installed run-study files and the target's own files, ran one study from intake to a committed record that passes the record checks. A second fresh agent then read only that record directory and wrote the synthesis. No cut was applied: the agent wrote the annex, manifest and axis declaration itself.

## Setup

- **Target.** `/tmp/study-dryrun-20261012/target`, built by `../setup_target.sh` without `--with-manifest`. The revisions are in `setup.md`: sysml-codegen `f44c991`, agentic-mbse `db032d6`, both installed as wheels built from `git archive`, on `/usr/bin/python3.12`; teax `8d87746`. The ready-made pieces were `models/`, `station.snapshot.json`, `pkg/station_study/`, `studies/study_route.py` and `studies/oracle_entry.py`.
- **Isolation.** `claude -p … --setting-sources project,local --permission-mode acceptEdits --allowedTools "Bash Read Write Edit Glob Grep Agent Skill" --output-format stream-json --verbose`, model `claude-opus-5-5`, the same mechanism as Item 2's dry run.
  - The init message lists the installed `run-study` and `teax-completion` and Claude Code's built-in commands. It lists none of the owner's user-level `_my_*` commands or skills.
  - The administrator ran without `Agent` and `Skill`.
- **The agent's reads.**
  - 6 Read/Glob/Grep targets: the installed skill's four files, the target's `STUDY_POLICY.md`, and the installed `verify.py` in the venv.
  - 30 Bash commands, none naming an absolute path outside the scratch area.
  - No fusion-tea path appears anywhere.

## What happened

1. **Run 1** (`study-agent-result.md`, $1.91).
   - The agent wrote the annex and manifest from the model file, marked as its own and unapproved, and filled the policy's Locations and route sections from the operator's answers.
   - It ran indicators, baseline, preflight (all six gates) and the oracle scan.
   - At step 7 it hit a question only the operator could answer, wrote it in § 17, committed record `20261012-pump-fit-response` (`5eb5dbb`) and stopped, as the brief's stop rule says.
   - The question: the named route's fixed grid holds energy price at 0.10, so the "proceed as sensitivity-only" ruling cannot be carried out through it. The agent also noted that the grid was fixed in route code before the oracle scan.
2. **Operator answer** (`operator-answer-1.md`). Run basin area × capacity only, and answer energy price by its indicator. Accept the route's pre-set grid as the window, recorded as such.
3. **Run 2** (`study-agent-2-result.md`, $3.07).
   - The committed record is immutable under the runbook, so the agent appended an addendum to it and ran a new record, `20261012-pump-fit-response-b` (`ec99f16`), through steps 1–15.
   - 12 points: 7 satisfied, 5 violated, each re-derived and matched to the independent oracle at 0.0 deviation.
   - § 14 holds each step-14 and step-15 Check command with its output (`[]`, `0`, `[]`, `[]`, `[]`).
4. **Record check.** `python3 ../check_record.py …/20261012-pump-fit-response-b` passes all five checks, exit 0, and agrees with § 14. Every tool document carries `tool.path` under `sysml_codegen/study/`: `indicators.json`, `results/preflight_results.json`, `results/postrun_clean.json`, `results/verification_summary.json`.
5. **Administrator** (`admin-agent-result.md`, $0.95).
   - It read only `record.md`, `snapshot.json`, `indicators.json` and `results/`, and checked every digest against `snapshot.json`.
   - It wrote `synthesis.md`. `git status` showed that file alone.
   - It listed missing facts as missing, without looking them up. It flagged one sentence in `results/report.md` that states the energy-price finding more absolutely than the structural check supports.

## Findings for the item and its follow-ups

- **F-DR1 · No resume path for a stopped record.** The runbook has a § 17 stop rule but does not say how a stopped record resumes. The agent obeyed immutability and started a new record id, which is defensible but costly. This text came over unchanged from fusion-tea's runbook. Filed as a follow-up, not changed in this item: changing the record lifecycle is outside the closed list.
- **F-DR2 · The fixture's route fixes its grid in code.** That clashes with the runbook's rule that the study window is fixed after the oracle scan, and it can't run a sensitivity-only axis. It is a property of the neutral fixture's `study_route.py`, not of the shipped text. A follow-up could give the fixture route a points-based entry, so a future dry run needs no operator ruling.
- **F-DR3 · Report wording.** The executor's `results/report.md` overstated the structural energy-price result. The administrator reading caught it, which is the role working as the owner intended. No change needed.

The copied records are in `target-studies/`, and the target's filled policy is in `target-STUDY_POLICY.md`.
