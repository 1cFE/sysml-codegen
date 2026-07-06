# Audit: docs-scrub

**Verdict:** Certify
**Audited:** 2026-07-06
**Branch:** `docs-scrub`
**Commit:** c45a836 (+ audit-cure commit following)

---

## Summary

The scrub delivered what the spec asked: all 31 docs/architecture files verified against
epic HEAD via a single ground-truth fact sheet, the matrix recounted from actual rows
(and extended with three REQ families the epic defined in docs but never added), the
contract doc coherent, thin prose closed, and the gate byte-identical. An independent
adversarial audit (separate agent, instructed to falsify each criterion) returned
**Needs Work** with three docs-only gaps; all three were cured and re-verified before
this certification.

## Findings

### Plan completion

All five phases verified complete; per-doc status tables have no empty cells. The
Phase-5 "capture-workflow docs state the split" checkbox was checked before the docs
actually said it at *script* level (auditor finding 5) — cured, see below.

### Spec conformance

- Every docs/architecture file read against HEAD — VERIFIED (13 scrub agents + auditor
  spot-checks; doc 24 clean on 14 claims; docs 22/23 spot-checks clean).
- Matrix summary recomputed from rows — VERIFIED (248 = 236 PASS + 12 UNTESTED; 29
  families; 54 distinct test files; all Index counts match; REQ IDs unique; every cited
  test file exists).
- modeling-assumptions coherent end-to-end; EXPOSE one story — VERIFIED (auditor traced
  §3/§5/V-table claims to `data_models.py`, `output_registry_builder.py` Phase 3b,
  `pipeline_builder.py` precedence tiers; no V12/V13 strings in src/).
- Thin docs 07/10/11/17/24 describe current behavior — VERIFIED after cure. **Auditor
  gap (major):** doc 10 + matrix REQ-OR-05/08 asserted Key_A/Key_F are "not registered"
  while `build_output_registry()` registers both (Key_A as alias, Phase 1a; Key_F as
  scoped, Phase 1c). Cured docs-only: a "Known divergence at HEAD (DOCS-SCRUB-F2)" note
  in doc 10's Eliminated Key Formats section, corrected verified-by cells, and NOTE
  annotations on the two matrix rows. The substantive reconciliation stays filed as
  BACKLOG `DOCS-SCRUB-F2` (not a docs-only fix).
- No pre-epic names — VERIFIED (`ConsumerScopedKey` absent from docs/, CLAUDE.md, src/).
- Capture-workflow license split — VERIFIED after cure. **Auditor gap (minor):** the
  split was stated only at CLI level; the spec requires script level. Cured: script-level
  paragraphs added to docs 27 and 00 naming all three scripts.
- Docs 22/23/26 verdicts — VERIFIED (22 live/corrected, 23 live/corrected, 26 Historical
  banner; end states checked against code).
- CLAUDE.md snapshot/`--from-snapshot` — VERIFIED against `cli/`, `snapshot/serializer.py`,
  `snapshot/loader.py`.
- Symbol anchors — VERIFIED (zero `.py:NNN` / `.jinja2:NNN` anchors anywhere in docs/).
- Gate unchanged — VERIFIED twice (before and after the audit cure): 1989 passed /
  4 skipped / 5 xfailed; ruff src/ 21; mypy src/ 109. Docs-only diff proof:
  `upstream-findings-epic...docs-scrub` touches only docs/, .project/, CLAUDE.md.

**Auditor gap (moderate), cured:** overview.md's verification counts (written before the
matrix gained the SNAP/NC/REG rows) contradicted the shipped matrix. Cured by removing
hardcoded counts from overview.md in favor of a pointer to the matrix — counts now have
one home, killing this drift class.

### Design conformance

N/A (no design stage; spec → plan → implement → audit, per spec).

### Code integrity

Docs-only change; no code touched (proof above). Code smells found *while verifying docs*
were filed, not fixed: BACKLOG `DOCS-SCRUB-F1` (two dead templates + four dead-code
candidates), `F2` (Key_A/Key_F REQ reconciliation), `F3` (four stale code docstrings),
`F4` (`resolve_input()` has zero production call sites while REQ-IR-05/07/REQ-RES-02
mark it PASS — the scrub's biggest code-side finding).

---

## Certification

Checked: all spec success criteria (each traced above), all plan checkboxes and status
tables, the three independent-audit gaps and their cures, and the gate (twice). Marked:
spec success criteria → [x]; plan status → Complete (certified); CURRENT_WORK updated.
Left open (deliberately, as filed backlog items, not gaps in this work): DOCS-SCRUB-F1
through F4.
