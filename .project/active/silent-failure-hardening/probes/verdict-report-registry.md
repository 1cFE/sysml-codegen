# Verdict: Gated-Report Silences + Registry Skips + Exception Swallows — Item 5

Findings D3-4, D3-5, D3-6, D3-12, D3-13, D3-14, and the pattern-3 family. This verdict was
completed by the orchestrator via code trace after the assigned probe agent was cut off by
a rate limit; the probe scripts it wrote (`probe_d3_4_discarded_report.py`) are committed.

**Execution note.** Python execution is blocked at the permission layer in this sandbox
(same wall as all four agents). These are deterministic terminal-arm bugs, so a full code
trace is airtight. Verdicts below cite file:line traced directly.

## D3-4 — usage-extraction warning report discarded (live path)
- **Intended:** the report exists to surface dropped usages ("could not resolve calc def").
- **Trace:** `pipeline_builder.py:689` — `calc_usages, _report = extract_calculation_usages(…)`;
  `_report` is bound and never used. Its "usage dropped from pipeline" warnings never reach
  the user.
- **Verdict: CONFIRMED.** Gated-report silence, headline. Choke: thread and emit the report.

## D3-5 — Registry Phase 1a unknown calc def → bare `continue`
- **Intended:** `10-output-registry.md` Phase 1a registers every CalcUsage's channels.
- **Trace:** `output_registry_builder.py:167-168` — `if not calc_def: continue`, no logger.
- **Verdict: CONFIRMED.** Zero channels, no log. Choke: warn on the skip.

## D3-6 — snapshot loader `except (JSONDecodeError, IndexError): pass`
- **Intended:** `27-snapshot-generation.md` — offline path reproduces live wiring.
- **Trace:** `snapshot/loader.py:423-424` — malformed `usage_type_map` key silently dropped
  → retype falls back to base def, offline-only mis-wire.
- **Verdict: CONFIRMED-latent** (offline-parity guard; trip needs a malformed snapshot key).
  Choke (Family 4): loud skip-with-warning.

## D3-12 — default-expr eval `except Exception: return None`
- **Intended:** `17-parameter-group-deriver.md` — an unevaluable default is a gap to surface.
- **Trace:** `parameter_groups.py:192-193` — bare `except Exception: return None`; `None`
  default → param omitted from its group with no diagnostic.
- **Verdict: CONFIRMED.** Choke (Family 4): warn + typed absence.

## D3-13 — phantom detector blindness reads as "no phantoms"
- **Intended:** distinguish "clean" from "couldn't scan".
- **Trace:** `phantom_detector.py:165-173` — `calc_def_map.get(usage.calc_def_name)` miss
  silently omits that usage's outputs from `_output_names`; a broken scan is byte-identical
  to a clean model.
- **Verdict: RECLASSIFIED → sentinel.** Not a reproducible wrong-output bug; wants a
  zero-found "scanned N, matched 0" sentinel (Family 2).

## D3-14 — `--smart-regen` transient error → silent stub regen
- **Intended:** `23-smart-regen-preservation.md` — never lose a valid impl on a transient error.
- **Trace:** `preservation.py:93-96` — `except SyntaxError: return None` /
  `except Exception: return None` (not even DEBUG-logged) → treated as "nothing to preserve"
  → stub overwrite. `cli:397` drives the regen.
- **Verdict: CONFIRMED.** Choke (Family 4). **Split candidate** — see spec Open Questions.

## Pattern-3 family — zero-found sentinels
- **Sites (traced):** scoped-alias registration `pipeline_builder.py:463-510` (INFO at 510);
  self-named rescue `:516-572` (INFO at 572 only if `rescued>0`); design-override rewrite
  `:259-329` (bare-name skip DEBUG at 309); template detection
  `usage_extractor.py:439-445`; empty-render success `cli:432-442`.
- **Shared shape:** the diagnostic is gated on a collection that shares the collector's
  failure mode — when the collection is empty for the *wrong* reason, the pipeline is silent.
- **Verdict: CONFIRMED (family).** Choke: adopt the `render_constraint_report` sentinel style
  (`constraint_report.py:89-141`) — always-present scanned/reported/excluded line.

## Family choke points
- **Gated-report silences (D3-4, D3-5, D3-13, pattern-3):** surface the report; add
  "scanned N, matched 0" sentinels in the Item-4 house style. Zero-found ≠ silence.
- **Exception swallows (D3-6, D3-12, D3-14):** narrow each `except`, log at WARNING, surface
  the skip; distinguish transient from genuine-empty for D3-14.
