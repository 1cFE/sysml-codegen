# SC4 dry run: the study agent's brief

This is design Appendix H2 step 3's brief, with the § 17 stop rule and step 4's Check instruction. The text between the two rules below goes to the agent as written. Everything outside them is for the orchestrator.

## For the orchestrator

1. **Target.** `setup_target.sh SCRATCH CODEGEN_REPO AGENTIC_REPO TEAX_CHECKOUT`, or with `--with-manifest` under cut 3. Its `SCRATCH/setup.md` names the revisions and the pieces supplied ready-made.
2. **Agent.** Run `claude -p` in `SCRATCH/target`, in a shell that sourced `SCRATCH/env.sh`, with stream-json output so the read-file list can be taken from the transcript. No user-level instructions, skills or memory may reach the agent, and authentication must still work. Item 2's dry run left the mechanism to the orchestrator at run time; record the one used, and the user-level configuration the transcript's init message shows the agent could see.
3. **Under cut 3,** add the bracketed line in the operator's answers. Without cut 3, leave it out.
4. **Afterwards,** run `python3 check_record.py SCRATCH/target/studies/<study-id>` (H2 step 4). Compare its verdict with the Check outputs the agent recorded in the record's § 14; any disagreement is a finding. Then run the administrator brief (`administrator-brief.md`), unless cut 4 applies.

**Expected observations (O2):**

- A committed record exists under `studies/<study-id>/`.
- The record's § 14 holds each step-14 and step-15 Check command and what it printed, and `check_record.py` passes and agrees with them.
- Every tool document in the record carries a `tool.path` under `sysml_codegen/study/`.
- The read-file list holds only target files, the installed skill and the venv. Reads under `TEAX_SIMKIT_PATH` are teax, the runtime the route runs on, and are listed as such.
- The ready-made pieces are the ones `setup.md` names; the annex, the axis declaration and (without cut 3) the manifest were written by the agent from the installed text.

---

Study how the pump-fit constraint responds to basin area and installed pump capacity, and whether the energy price matters to it. The package is pkg/station_study.

Use the run-study skill installed in this project, with the runbook, templates and integration guide beside it, and the study policy at `modeling_project/STUDY_POLICY.md`. Work from those and from this project's files only. The study tools are installed: run them as `sysml-codegen study <tool>`.

Your operator has already answered these questions, so do not ask them:

- The studies directory is `studies/`. Write that into the policy's § Locations.
- The execution route is `execute_baseline` and `run_grid` in `studies/study_route.py`.
- The oracle is `oracle_entry`, in `studies/`.
- If an axis reports `no_constraint_response`, the ruling is: proceed with it as sensitivity-only.
- A coordinator review check suffices for the review steps.
- Commit the record.
- [Cut 3 only:] `studies/manifest.json` is supplied. Use it as it is; do not write a manifest.

For anything else, write it under § 17 and stop. That means: if you reach a question only the operator can answer, write the question in the record's § 17 "What this record does not contain", commit what you have, and stop. Do not guess the answer, and do not ask.

At steps 14 and 15, run each **Check:** line the installed runbook gives, from the record directory, and record each command with what it printed in the record's § 14, as the runbook says.

---
