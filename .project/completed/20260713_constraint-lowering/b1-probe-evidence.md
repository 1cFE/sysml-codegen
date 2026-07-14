# B1 Probe Evidence — Per-Occurrence Producer Channels (orchestrator, 2026-07-12)

Probe: `probe_b1_channels.py` (this directory), run via `uv run python` in this repo (licensed).
Model: `Cell` owning `power_calc : 'Power Calc'`; `Container { part cell : Cell[3]; }`;
package-level design instance (required for instantiation-path discovery — a def-only model
drops the template calc entirely: "no PartUsage instantiations").

## Observed

- Canonical producer channels for the `[3]` part's calc: **exactly one** —
  `MultiChan__the_design__c__cell__power_calc__p`; one scoped key
  (`the_design.c.cell.power_calc.p`, dotted, **no occurrence index**).
- `PartInstanceIndex.occurrences_of("MultiChan__Cell")`: **three** occurrences
  (`…c__cell[0..2]`). Singleton control: identical single channel.
- Occurrence-indexed lookups (`…cell[0]…`) MISS (None); the de-indexed form is the only hit.

**B1 is refuted**, exactly as the design review's static trace predicted: the calc pipeline
does not fan fixed multiplicity; per-occurrence producer channels do not exist.

## Orchestrator adjudication (agent-grade — binding on the design revision)

The review's "S5 unmeetable" framing over-reads S3 carry-forward (3). Its "three occurrences
are three wired modules, not copies" concerns the **constraint modules' own identity and
output channels** — achievable regardless of producer sharing. The corrected semantics:

1. Per-occurrence expansion stands: three `ConcreteConstraint`s, three IDs, three catalog
   entries, three constraint modules each with their own output channel.
2. Actual resolution binds what the registry actually holds. The ordered procedure tries the
   occurrence-scoped key first; when only the shared (de-indexed) producer channel exists,
   binding it is the model's true semantics — sibling calcs are one module today — and is
   **recorded per-occurrence in the catalog entry** (which channel each occurrence bound), so
   shared-producer verdict-equality is visible data, never silence.
3. Growing per-occurrence CALC producers is **out of scope** for Item 5 (a calc-pipeline
   capability change, not constraint lowering). Named limitation with a relaxation path,
   mirroring the epic's other first-scope blocks. Where the model genuinely differentiates
   occurrences (per-occurrence redefined attributes → distinct design attributes), strict
   resolution wires them distinctly with no new machinery.
4. The multi-instance success criterion is met by: 3 IDs / 3 entries / 3 modules with own
   channels + recorded (possibly shared) producer bindings + a fixture asserting exactly that.
