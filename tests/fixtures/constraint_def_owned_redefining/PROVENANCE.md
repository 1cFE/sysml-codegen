# Provenance

New fixture for CONSTRAINT-LIFECYCLE Item 13 (composed proof), Appendix C **case 18**
("Definition-owned assert through redefining usage"), authored per the evidence-coordinate
register's "author if absent" instruction (Stage 2 execution, 2026-07-20).

## What it proves (coordinate)

The `part def Panel` **owns** the assertion (`assert constraint within : 'Within Limit'`,
typed by a shared constraint def). The nested design attribute `source.reading` is declared
without a value binding and is **redefined at the usage** via `:>> source.reading = 80.0`.
The coordinate: the definition-owned assert SOURCE and the redefining occurrence's actual
identity remain **distinct** (invariant 27), and the sealed thread yields the expected
verdict (`reading = 80.0` satisfies `v <= 100.0`).

Follows the `constraint_occurrence_demand/order` idiom (nested `Source` part, plain attribute,
redefined at the usage).

## Validation at authoring (pin `7526665`, licensed)

`sysml-codegen generate --models tests/fixtures/constraint_def_owned_redefining` **parses** and
**extracts** the redefinition (Step 3.5 reports "1 design overrides"). Full generation then
**halts** at constraint-actual resolution: `panel.v: unresolved actual 'source.reading'
(strict mode: no fallback, no entry-point synthesis — INV-2)`. This is the same class as the
sibling `order`/`overrides` redefinition probes, which also halt generation and are exercised
at the extraction/acceptance level.

## SURFACED (capture-fidelity law 4 — do not resolve silently)

Case 18's coordinate says the redefining-usage actual should resolve and **produce the expected
verdict**. At pin `7526665`, a `:>>`-redefined design attribute feeding a constraint actual is
**not minted as an entry point** and the actual does not resolve at generation under strict
INV-2. Whether this is (a) intended — the compose stage supplies the cross-part wiring
(Items 9–11) — or (b) a finding returned to Item 2 (the owning row) is for the **compose stage**
to determine. Stage 2 (reruns) authored the fixture and surfaced this boundary; it did not fix
production code (per the stage's discipline).

## Classification note

Case 18 is **compose**-classified in the manifest. This session authored the fixture only.
