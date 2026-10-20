The audit (`audit.md`) is Needs Work with one blocker. Fix it and the advisory points below; commit each fix with its tests, update plan notes, and run the exit check.

Blocker (RG-1 territory, owner-ratified rule): `generate` imports agentic-mbse's `subset_profile` via `cli/readiness.py:29` before loading the model; if that import fails, `generate` crashes and writes nothing. Fix it by structure, not by a try/except around the top-level import: nothing on `generate`'s route before the seal may import agentic-mbse's screen or anything that imports it. Import `readiness`/the screen only inside the after-seal guard (and inside `check`'s screen step, where a failure becomes "not assessed"). Add a test that makes the screen module fail to import (a real import failure via `sys.modules`/meta-path, not a version-string patch) and checks: `generate` builds the same bytes as base and reports the screen not assessed; `--from-snapshot` likewise; `check` reports the generator's answer with the screen not assessed and exits 3, not a crash. Extend the import-boundary test to cover `readiness.py`. Then re-read Success Criteria 7 and 8 and make sure their named tests now prove what the words claim.

Advisory points — fix these too, the bar is clean code:
- The report labels environment failures "refused". Use the design's "environment failure" outcome.
- Spec Criterion 10 says "every finding"; update its wording to match the Phase 8 follow-up display ruling (all findings collected and counted; actionable ones printed in full). This is a wording fix recording an orchestrator decision, not a scope change.
- The package name carried twice and kept in step by a runtime `ValueError`: carry it once if the change is small and clean; otherwise say why not.
- The error-handling ladder copied three times across the pipeline builders: factor it if it is the same logic; if the copies differ meaningfully, say how and leave them.
- Move the read-only destination check out of `emit.py` if that makes "check never imports the writing module" true by structure; otherwise say why not.
Report what changed.
