# SC4 dry run: the administrator's brief

This is design Appendix H2 step 5: a cold reading of the committed record. Cut 4 skips it. The text between the two rules below goes to the administrator as written. Everything outside them is for the orchestrator.

## For the orchestrator

- Run it after the study agent has committed its record and `check_record.py` has run.
- Start a fresh `claude -p` session in `SCRATCH/target`, with the same isolation as the study agent and nothing from the study agent's session. Replace `<study-id>` below with the record's directory name.
- **Expected observations:** `studies/<study-id>/synthesis.md` exists, written as the installed runbook's "Administer" section says. The read-file list holds the installed skill and files inside the record directory only. Nothing else in the target changed: `git status --short` lists `synthesis.md` alone.

---

You are the administrator of a finished parameter study. Its record is the directory `studies/<study-id>/` in this project.

Read the run-study skill installed in this project and the "Administer" section of its runbook. Then read the record directory, and only the record directory: `record.md`, `snapshot.json`, `indicators.json` and `results/`. Do not open anything else in the project. That includes the package, the manifest, the route, the oracle, the discovery log and the study policy.

Write `synthesis.md` in the record directory, as the "Administer" section says. Write nothing else, and change no other file.

A fact you cannot recover from the record directory goes in the synthesis's "What the record does not support", as missing. Never recover it from anywhere else.

---
