# Provenance — sibling-formal collision producer cycle (spike `s5_sibling_formal`)

Promoted for self-binding-replacement Phase 1 from the spike fixture
`.project/active/self-binding-replacement/spike/fixtures/s5_sibling_formal/` (findings F-3).
Package renamed `S5SiblingFormal` → `sibling_formal_cycle` and the part def unquoted; the
shape is otherwise unchanged.

## Measured behavior

The D-5 rename residual risk: the calc def already declares an `out` member carrying the part
attribute's bare name, so the renamed binding's bare right-hand side `availability` resolves
onto the calc's own output. The input consumes its own calculation's output — a typed producer
dependency cycle.

- **Pre-repair (`0f89673`):** a raw `GraphValidationError: SI_EDGE_DANGLING: typed producer
  dependency cycle` traceback escaped `elaborate()` through `run_codegen` — loud, but naming
  no file, no binding, and no participant
  (`.project/active/self-binding-replacement/verification/post-repair-spike-recheck.md`, F-3).
- **Post-repair:** final graph validation surfaces as `ElaborationDiagnosticError`; the cycle
  diagnostic names its participants in stable order, and `generate` exits 1 with the typed
  message and no traceback.

Owner class: n/a — the right-hand side resolves to the consumer's own sibling formal, not to
an occurrence-owned feature, so no D-6 position claim attaches.

Kept tests: `tests/conformance/test_elaboration_cycle_diagnostics.py`.
