
Study how the pump-fit constraint responds to basin area and installed pump capacity, and whether the energy price matters to it. The package is pkg/station_study.

Use the run-study skill installed in this project, with the runbook, templates and integration guide beside it, and the study policy at `modeling_project/STUDY_POLICY.md`. Work from those and from this project's files only. The study tools are installed: run them as `sysml-codegen study <tool>`.

Your operator has already answered these questions, so do not ask them:

- The studies directory is `studies/`. Write that into the policy's § Locations.
- The execution route is `execute_baseline` and `run_grid` in `studies/study_route.py`.
- The oracle is `oracle_entry`, in `studies/`.
- If an axis reports `no_constraint_response`, the ruling is: proceed with it as sensitivity-only.
- A coordinator review check suffices for the review steps.
- Commit the record.

For anything else, write it under § 17 and stop. That means: if you reach a question only the operator can answer, write the question in the record's § 17 "What this record does not contain", commit what you have, and stop. Do not guess the answer, and do not ask.

At steps 14 and 15, run each **Check:** line the installed runbook gives, from the record directory, and record each command with what it printed in the record's § 14, as the runbook says.

