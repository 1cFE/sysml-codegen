# Design: Self-Binding Replacement — Establish, Document, Migrate

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-15
**Stage:** `design` (orchestrated run; orchestrator brief `briefs/04-design.md`)
**Repo state:** codegen `main` @ `c334bdf`; working tree carries the uncommitted `dead-worktree-pins` edits
**Complexity:** MEDIUM

---

## Overview

Teach one situational rule for binding a modelled value into a calculation, hold it in exactly one
authoritative document, reach every surface that instructs a human or an agent, migrate the 15
fusion-tea self-bindings to the ratified D-5 form with a mechanical proof that only the referent
changed, and prove the value now arrives by mutation.

## Related Artifacts

- **Spec:** `.project/active/self-binding-replacement/spec.md` (rev 3)
- **Measured authority:** `.project/active/self-binding-replacement/spike/findings.md`
- **Dispositions:** `.project/active/self-binding-replacement/briefs/03-spike-dispositions.md`
- **Align record:** `.project/active/self-binding-replacement/briefs/00-align.md`
- **Design brief:** `.project/active/self-binding-replacement/briefs/04-design.md`
- **Scope context:** `.project/research/20260815-103905_item8-bounded-stocktake.md`
- **Contract (D-4…D-7):** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:604-627`
- **Product lens:** `.project/active/self-binding-replacement/product-lens.md` — rev 3 `Gate: CLEAR`,
  with smell 7 flagged forward to design review (below, "Where smell 7 could bite")

---

## The Point

A modelled value bound as `in availability = availability` never reaches the calculation. The
right-hand name resolves to the calculation's own input parameter, so the calculation computes on a
default and returns a confident wrong number. Legal SysML, silently inert.

That is the direct negation of the product's promise. `P-001` says a designer varies parameters
freely and gets a viability answer they can trust. If a varied parameter never arrives, the answer is
wrong and nothing says so. The epic's critical success factor, owner grade
(`.project/backlog/epic_elaborate_first_architecture.md:31-33`), states it as: every consumed
modelled value resolves to exactly one runtime source across all bound consumers, and an unsupported
authored form fails loudly before generation. The `[OWNER]` mission invariant at `:84-86` adds the
observable: a public mutation reaches **every and only** the bound consumers.

The owner restated the obligation verbatim on 2026-08-15:

> "We know what the RIGHT pattern(s) are for the given situation / We document those right patterns /
> We fix the models to use the right patterns. `in R = R` is the wrong pattern. I would like to
> detect the use of it so we avoid it in the future."

Four clauses, and the deliverable is all four. Generation and seal are necessary evidence, not the
goal. The goal is that the rule is known, written where humans and agents read it, applied to the
models, and the wrong form confirmed refused before generation.

---

## Research Findings

### The companion repositories were unreadable this session — and it did not block the design

This session's sandbox refuses `ls`, `find`, `git`, and `Read` outside `/home/reid/1cfe/sysml-codegen`,
including through `.claude/`'s resolving symlinks. Two substitutes carried the evidence:

- **`.venv/.../site-packages/agentic_mbse_data/`** is the live agentic-mbse source, not a stale copy.
  `stat` reports link count 2 on `docs/patterns/plant-idiom.md` and
  `claude/skills/sysml-conventions/SKILL.md` — they are **hardlinks to the source inodes**, installed
  today at 08:17. Every `claude/` and `docs/patterns/` measurement below is therefore current.
- **`reverted/fusion-tea-model-migration.patch`** carries all 15 customer sites verbatim with
  context, so the migration was designed against the real lines.

What remains unverified: `agentic-mbse/.claude/` (23 files, 4 skills) is not packaged and was not
readable. See "Potential Risks" — the plan must repeat one grep there.

### The agent-instruction surface is one file, measured

Across the whole packaged `claude/` tree (5 agents, 15 commands, 10 skills), the count of lines
matching `^\s*in\s+\w+\s*=` — a calculation-input binding example — is:

| surface | binding examples |
|---|---|
| `claude/skills/sysml-conventions/SKILL.md` | **4** |
| every other file in `claude/` (agents, commands, other 9 skills) | 0 |

The four in the skill are constraint bindings, all correctly named-differently
(`in temperature = reactor.wall_temperature_k`, `in actual = pumping_speed_total`). The skill needs
an **addition**, not a correction.

Searching `claude/` and `docs/` for `self-named`, `SI_SELF_BINDING`, `L2_SELF_NAMED` returns hits in
**one file only** — `docs/patterns/plant-idiom.md`. This reconfirms the spec-review gap at HEAD: no
agent surface warns about self-binding.

### The four refused examples, located exactly

`grep -P "in (\w+)\s*=\s*\1\s*;"` over `docs/patterns/` returns four hits, all in `plant-idiom.md`:

| line | example | situation |
|---|---|---|
| 79 | `calc base_power_calc : DriverPowerCalc { in bank_energy = bank_energy; }` | D-5 (own attribute) |
| 84 | `in cost_per_joule = cost_per_joule;` | D-5 |
| 85 | `in bank_energy = bank_energy;` (inherited attribute) | D-5 |
| 200 | `in throughput = throughput;` (the EXPOSE example the brief names) | D-5 over an EXPOSE |

Zero hits in the other seven pattern docs that carry binding examples (`expose-pattern.md` 14,
`cross-file-binding.md` 15, `syntax-reference.md` 4, `common-mistakes.md` 4, `constraints.md` 3,
`semantic-operators.md` 2, `adr002-calculations.md` 2). "No contradictory guidance left behind" is
therefore a bounded edit, not a sweep.

`plant-idiom.md:57-62` is the guidance the spec calls situationally silent: two spellings of one
local fix, one sentence about another part, no rule.

### The migration target is already worked, in this repo

`tests/fixtures/fusion_tea/` is the customer model **already D-5 migrated**. It renames **11 distinct
formals** across three library definition files and rewrites **15 usage binding left sides** across
the same three design files the brief names:

- `library/analyses/ife_lcoe.sysml` — `availability_in`, `discount_rate_in`, `frequency_in`,
  `gain_in`, `om_cost_constant_in`, `plant_cost_constant_in`, `thermal_efficiency_in`
- `library/analyses/hif_economics.sysml` — `beam_energy_mj_in`, `num_chambers_in`,
  `thermal_power_gw_in`, `availability_in`, `net_electric_power_gw_in`
- `library/analyses/fusion_cycle.sysml` — `gain_in`, `thermal_efficiency_in`, and a **`constraint def`**
  formal `gain_in` at `:47`
- `designs/generic_ife/ife_plant.sysml` (10), `designs/hif_ife/hif_driver.sysml` (2),
  `designs/hif_ife/hif_plant.sysml` (3)

⚠ **The brief's site list is incomplete, and this is a scope correction rather than a premise
conflict.** D-5 renames the *formal*, so the `calc def` / `constraint def` that declares it must be
edited too. The brief names only the three design files. `make_d5_variant.py:203-229` already
implements both halves, and the fixture proves the result elaborates. Nothing upstream is falsified;
the enumeration just has to grow by three library files.

### F-3 is contained — located precisely

The spike's raw traceback has one cause, one line:

- `elaborate.py:631` calls `self._graph.validate()` **outside** any handler. `validate()` raises
  `GraphValidationError` directly at `graph.py:448` when it collects failures, so it never reaches
  the `ElaborationDiagnosticError` raise two lines below at `:632-633`.
- The CLI catches `ElaborationError`, `ElaborationDiagnosticError`, `SysMLParsingError`,
  `CodeGenerationError`, `InstanceGraphSnapshotError` (`cli/__init__.py:1191-1212`).
  `GraphValidationError` is a bare `ValueError` and is in none of them, so it escapes as a traceback.
- The message names nothing because `_graph_failure` (`graph.py:944-952`) mints the cycle diagnostic
  with `consumer=None`, `consumer_display="<instance-graph>"`, and no participants.

Both halves are repairable inside two methods. This is a boundary repair, not graph restructuring.

### Prior decisions consulted

`.project/adr/INDEX.md` does not exist. Per `CLAUDE.md`, an ADR is a numbered section of
`docs/architecture/modeling-assumptions.md`; nine exist, next free id ADR-010. None covers binding
resolution — the "Validation Rules" table (`:747`) lists V1–V11 and does not mention
`SI_SELF_BINDING`.

---

## Core Concept

**One rule, one copy, three legs of enforcement.**

The rule is situational and short: *a calculation input binds to the modelled value you name, and the
name is resolved from where the consumer sits.* Three situations follow from where the value lives.
The value is an attribute on the part owning the calculation → make the two names differ and bind
bare (D-5). The value lives on another part → name the occurrence path (D-7). You reach by owner
qualification (D-6) → it resolves by your **position**: if your own scope lineage owns the slot you
win outright however many occurrences exist; otherwise the route searches descendants innermost-first
and refuses as ambiguous only on a collision — which also means it reaches *sideways* into a sibling
subtree when exactly one occurrence lives there. Owner qualification does not mean "mine."

That rule lives in exactly one document, `agentic-mbse/docs/patterns/plant-idiom.md`, reorganized by
situation. Everything else points at it. The two-copies trap that Item 7 left as residual A-1 is not
fought by synchronizing copies; it is dissolved by there being one copy to reach.

Three legs then keep the rule honest, and each is owned by a machine rather than a reader:

1. **The generator refuses the wrong form** — already shipped (`SI_SELF_BINDING`), confirmed on both
   paths, not rebuilt.
2. **Every published example is provenance-linked to a tracked fixture the shipped route actually
   elaborates or refuses**, so "parser-validated" is discharged by a passing test rather than by a
   snippet harness that proves only that text parses.
3. **The migration's proof is a strip check** — undo the renames and the original must return byte
   for byte, so a stray reformat or a nudged constant cannot ride along inside a large diff.

Why this is right and not merely workable: the failure this item exists to end is *a document that
teaches what the product refuses*. Any design that keeps the teaching in more than one place, or that
validates examples by reading them, reproduces that failure in a new spot. Pinning each taught shape
to a fixture makes the documentation falsifiable by CI instead of by review.

---

## Key Bets

- **B1.** The packaged `agentic_mbse_data` tree is byte-identical to the agentic-mbse working tree
  (hardlinked, link count 2, installed 2026-08-15 08:17). *If false → the surface inventory above is
  stale, and the rollout can miss a file that teaches the refused form.*
- **B2.** The customer `fusion-tea` library definitions are structurally the same definitions as
  `tests/fixtures/fusion_tea/library/analyses/*.sysml`, so the fixture is the worked target for the
  same 15 sites. *If false → the 11-formal rename set is wrong and must be re-derived from the
  customer tree before anything is written.*
- **B3.** No `calc def` or `constraint def` involved in the 15 sites declares a second member with the
  same bare name as a renamed formal (an `out`, or a second `in`). *If false → after the rename the
  bare right-hand side lands on that sibling formal instead of the outer attribute, producing spike
  row 5's cycle or row 7's `SI_OCCURRENCE_MISSING`, and that site needs D-7 instead of D-5.*
- **B4.** The measured resolution rule (position, not occurrence count) is the behavior of the route
  at the commit this item lands on. *If false → the rewritten guidance teaches a rule the shipped
  route does not implement, which is the exact defect being repaired.*
- **B5.** The entry-point key for a `DESIGN_ATTRIBUTE` is the supplying attribute's display path, so
  N consumers of one modelled value share one key. *If false → the "every and only" mutation check
  cannot be read off the entry-point set and needs execution-level evidence instead.*

## Key Decisions

- **D1. One authoritative copy: `agentic-mbse/docs/patterns/plant-idiom.md`, reorganized by
  situation.** Every other surface carries a pointer plus, at most, the one-paragraph rule.
  *Rejected: replicate the full rule into each surface* — that is the divergence the Item-7 A-1
  residual already produced once, and the counts (37 vs 23 files) show two trees drifting.
- **D2. The `sysml-conventions` skill carries the rule inline, briefly, as well as the pointer.**
  One row in its Common Pitfalls table, one short subsection stating the three situations, and a
  Reference-Files line to plant-idiom.md. *Rejected: pointer only* — the skill is what loads when an
  agent writes SysML; an agent that never learns the trap exists has no reason to go read about it.
  *Rejected: full teaching inline* — that is a second copy.
- **D3. Examples are validated by fixture provenance, not by a doc-snippet parser harness.** Every
  taught shape cites a tracked codegen fixture whose exact-route outcome a conformance test already
  pins. D-5 and D-7 are covered today by `tests/fixtures/fusion_tea`. D-6 is not, so three spike
  fixtures are promoted into `tests/fixtures/` (see Component Overview). *Rejected: extract and parse
  each fenced snippet* — parsing proves the fragment is legal SysML, which is precisely what the four
  refused examples already are.
- **D4. The migration is mechanized by `scripts/make_d5_variant.py`, extended with a `--root` so it
  can address a tree outside `tests/fixtures/`.** Build the variant into a scratch directory,
  strip-check it against the customer originals, and only then replace them. *Rejected: hand edits
  reviewed as a diff* — F-3's collision family and a stray reformat are exactly what a large diff
  hides. *Rejected: rewrite in place then check* — the check would then have nothing to compare to.
- **D5. A license-free collision precheck runs over the model text before any rename.** For each of
  the 11 formals: does its declaring def still declare a member of that bare name after the rename,
  and does it already declare `<name>_in`? Either answer stops the run. *Rejected: discover
  collisions by running the route* — the failure mode is spike row 5, whose current report names
  nothing.
- **D6. F-3 is fixed in codegen, in two contained places.** Wrap `elaborate.py:631` so
  `GraphValidationError` becomes `ElaborationDiagnosticError`, and make `_validate_producer_cycles`
  name the participating calculations. *Rejected: filing it* — the disposition said to file it only
  if it needed graph-layer restructuring, and the located cause is one unguarded call plus one
  diagnostic payload.
- **D7. F-2 is fixed in agentic-mbse only, by mirroring codegen's identity comparison.** Compare the
  referent element of the member's `feature_value_expression` to the member itself, instead of
  comparing `binding.source_path` to `binding.param_name` (`level2_structure.py:350`).
  *Rejected: special-casing qualified spellings by string* — the same class of name-based check that
  produced the false positive.
- **D8. The `hif_driver_instance` / R-2 acceptance pin is left exactly as it is.** *Rejected:
  re-anchoring it here.* The pin's subject is `tests/fixtures/fusion_tea` — which still declares
  `part hif_driver_instance` at `designs/hif_ife/hif_driver.sysml:100` and is untouched by this item.
  The 9-vs-11 channel question belongs to the customer-repo regeneration remainder, an explicit
  Non-Goal homed to `.project/active/elaborator-downstream/`. This is the smaller call and it does
  not contradict R-2.
- **D9. ADR-010 is filed** as `## 10. Calculation Input Bindings Resolve by Identity, Not by Name` in
  `docs/architecture/modeling-assumptions.md`, decision-and-consequence only, naming plant-idiom.md
  as the one home for worked examples. *Rejected: not filing it* — the refusal is a shipped product
  behavior that constrains every customer model, and no existing ADR or validation row covers it.
  *Rejected: filing the teaching text into the ADR* — that mints the second copy D1 exists to prevent.
- **D10. Stellarator gets one pipeline run, a written record, and a filed follow-on. Nothing is
  fixed.** *Rejected: migrating its 15 copied-in fusion-tea files while we are in there* — the July
  owner hold is not reversed by this item, and a partial migration would leave a model in a state
  neither the hold nor this item describes.

---

## Architecture

### Where each change lands

| repo | change |
|---|---|
| **agentic-mbse** | `docs/patterns/plant-idiom.md` rewritten by situation; four refused examples corrected; `claude/skills/sysml-conventions/SKILL.md` gains the rule + pointer; the same for `.claude/`'s counterpart if the inventory finds one; F-2 identity comparison in `validation/level2_structure.py` (+ `binding.py` if the referent must be exposed) with a test per direction |
| **sysml-codegen** (here) | F-3 repair in `elaboration/elaborate.py` and `elaboration/graph.py` + tests; three promoted D-6 fixtures + one conformance test; `scripts/make_d5_variant.py` gains `--root`; ADR-010 in `docs/architecture/modeling-assumptions.md` + a product-ledger row; the stellarator triage record and any filed follow-on |
| **fusion-tea** | 3 design files (15 binding left sides) + 3 library files (11 formal declarations and their in-body uses), on a branch off `item8-fusion-embedded-catalog` |
| **fusion-tea-stellarator-mbse-demo** | nothing. One run, recorded in codegen. |

Local commits only in every repo. No push, no PR (`briefs/00-align.md`, orchestrator boundary).

### The teaching, organized by situation

The rewritten `plant-idiom.md` self-binding section answers one question — *where does the value
live?* — and hands back one form:

1. **On the part that owns the calculation → D-5.** Rename the calculation's input and bind bare:
   `in availability_in = availability`. The bare name then lands on the outer attribute. A calc
   nested in the def gets one instance per occurrence, so this scales to repeated subsystems with no
   qualifier. Pinned by `tests/fixtures/fusion_tea` (spike row 2; mutation proved at row 2m).
2. **On a different part → D-7.** Name the occurrence path: `in driver_cost = driver.cost`. The
   reference lands on that occurrence's feature. Pinned by `tests/fixtures/fusion_tea`
   (`in driver_cost_constant = driver.cost_per_joule`; spike row 3).
3. **By owner qualification → D-6, and read the position rule before you use it.** Safe from inside
   the part definition, however many occurrences exist (spike rows 4a, 4b). From above, safe with one
   occurrence (4e) and refused as `SI_OCCURRENCE_AMBIGUOUS` with two (4c, 4d). And it reaches
   sideways: `'Unit'::cost` written where no local `'Unit'` exists resolves into a sibling subtree
   when exactly one occurrence lives there (F-4, spike row 6). Owner qualification does not mean
   "mine." The guidance states the rule and its reach; it does not recommend D-6 for the fusion-tea
   migration.

Plus the negative, kept and sharpened: `in x = x` binds the calculation's input to itself, is refused
by both paths, and is never reinterpreted as an outer reference (D-4, `[OWNER-VERBATIM]`).

Two authority corrections travel with the rewrite: SysML v2 Part 1 §7.17.2 is **not** cited as
authority for a shadowing rule (it is an action-parameter example and states no such rule), and the
`:>>` explanation cites KerML §7.3.4.5 for "the owner's own namespace excluded," with §8.2.3.5.1 as
the abstract-syntax mechanism.

### The migration, as a pipeline with a proof in the middle

```
collision precheck (license-free, text only)
      ↓  stops on a name that would land on a sibling formal
build variant into scratch  (make_d5_variant --root <fusion-tea>/models)
      ↓
strip check: remove `_in` everywhere → must reproduce the originals byte for byte
      ↓  any mismatch = something other than the rename happened; stop
replace originals, commit on a branch off item8-fusion-embedded-catalog
      ↓
generate + seal + snapshot, zero readiness diagnostics
      ↓
spine: mutate one migrated design attribute off default, regenerate, compare entry points
```

The strip check is the bounded-diff mechanism the spec asks for, and it establishes the right
invariant. The referent **must** change — that is the fix (product-lens `spec-F1`). What must not
change is everything else, and byte-identity-after-strip says exactly that about arithmetic, physical
values, comments, and formatting, without anyone reading a 26-line diff.

### The spine mutation check

`gain` is bound by three consumers in `ife_plant.sysml` (`:122`, `:146`, `:168`). Because a
`DESIGN_ATTRIBUTE` entry point keys by the **supplying attribute's** display path, all three
consumers share one key. So:

- change the modelled `gain` off its default in the migrated customer model;
- regenerate, and read `inputs/*.json` and `pipelines/pipeline.yaml`;
- **every**: the one entry point keyed on `gain` carries the new value, and all three consumer
  modules wire their `gain_in` formal to that key;
- **only**: no other entry point's value moves.

That is the epic's `[OWNER]` mission invariant read directly off shipped public artifacts, which is
what the spike established as sufficient at row 2m. It does not require TEAx execution.

---

## Required Invariants

1. **One authoritative teaching copy.** Exactly one document states the situational rule in full;
   every other live surface either points at it or carries a pointer plus the one-paragraph summary.
2. **Zero surviving `in x = x` examples** anywhere a human or agent reads — verified by the same
   `grep -P "in (\w+)\s*=\s*\1\s*;"` that found the four, run over both trees.
3. **Every taught shape is pinned by a tracked fixture** whose exact-route outcome (generates with a
   named entry point, or refuses with a named code) a conformance test asserts.
4. **The migration's only edit is the rename.** Stripping `_in` reproduces the originals byte for
   byte, file for file.
5. **The refused shape stays pinned.** `tests/fixtures/self_named_binding_trap`,
   `self_named_rescue`, and every other fixture that exists to prove refusal keeps carrying
   `in x = x`. They are not migration targets.
6. **No readiness diagnostic escapes as a traceback.** Every refusal the route reaches leaves the CLI
   as a named diagnostic with exit 1.
7. **Both validation paths agree on the self-named form**, and after F-2 they agree on D-6 as well —
   codegen accepts it and agentic-mbse stops flagging it.

---

## Component Overview

**agentic-mbse**

- `docs/patterns/plant-idiom.md` — the authoritative copy. Self-binding section reorganized by
  situation; the four refused examples at `:79`, `:84`, `:85`, `:200` corrected to the form that
  situation calls for; F-4's sideways reach gets its sentence.
- `claude/skills/sysml-conventions/SKILL.md` — one Common-Pitfalls row, one short subsection naming
  the three situations, one Reference-Files line. This is the only file in the whole `claude/` tree
  that teaches calculation bindings.
- `.claude/`'s counterpart surfaces — inventory first (the plan repeats the grep with repo access),
  then the same treatment for whatever it finds.
- `validation/level2_structure.py::check_self_named_bindings` — identity comparison replaces name
  comparison; `validation/binding.py` exposes the referent if needed. One test per direction:
  self-named still flagged, `'Plant'::availability` no longer flagged.

**sysml-codegen (here)**

- `elaboration/elaborate.py:631` — guard the `validate()` call; re-raise as
  `ElaborationDiagnosticError`, which the CLI already reports as "Model failed exact-route
  validation" with exit 1.
- `elaboration/graph.py::_validate_producer_cycles` — carry the cycle participants into the
  diagnostic so an author reading it knows which calculations closed the loop.
- `tests/fixtures/` — three promoted spike fixtures pinning D-6, each with a `PROVENANCE.md`: the
  inside-the-def two-occurrence shape that generates (spike `s4b`), the above-the-def two-occurrence
  shape that is refused (spike `s8`), and the sideways reach (spike `s6`). One conformance test
  asserts each outcome by name.
- `scripts/make_d5_variant.py` — a `--root` option so `FIXTURES` is not the only addressable tree.
  The recipe, the aggregation split, and the strip check are unchanged.
- `docs/architecture/modeling-assumptions.md` — ADR-010, plus its back-registered row in
  `.project/product/INDEX.md`.
- `.project/active/self-binding-replacement/stellarator-triage.md` — the one-run record.

**fusion-tea**

- `models/library/analyses/{ife_lcoe,hif_economics,fusion_cycle}.sysml` — 11 formal declarations
  renamed, with their in-body uses.
- `models/designs/{generic_ife/ife_plant,hif_ife/hif_driver,hif_ife/hif_plant}.sysml` — 15 binding
  left sides renamed.

---

## Non-Goals

- Reopening D-4 through D-7, or the choice of D-5 for the fusion-tea sites. D-6 turning out safer
  than the spec assumed is not a reason to prefer it.
- The rest of Item 8: the July IFE impact audit, certification repair, the composed proof thread, the
  fourteen-document rewrite list.
- The regeneration remainder — package/contract regeneration on the customer repo, duplicate-field
  workaround removal, study lineage, acceptance-pin re-anchoring. Homed to
  `.project/active/elaborator-downstream/`, which is deliberately not created here.
- Migrating or repairing stellarator, including its 15 copied-in fusion-tea files.
- Building any new detector, lint, or authoring-time check. Detection scope is confirm-what-ships
  (`briefs/00-align.md`).
- The second half of F-3 (`SI_OCCURRENCE_MISSING`'s bare `FeatureSlotId`) and F-5 (chain source
  paths). Both filed, not fixed.
- Any change to arithmetic, physical values, or model physics.

---

## Implementation Notes

- **Do not edit through the venv path.** `agentic_mbse_data/...` files are hardlinks to the
  agentic-mbse source. An editor that rewrites in place would silently mutate the source repo; one
  that writes a new file would break the link and leave a stale package. Read there, write in
  `/home/reid/1cfe/agentic-mbse/`.
- **The license is required** for every generate/seal/snapshot step:
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. A green run without it is not a run.
- **`make_d5_variant.py` needs formals supplied.** The customer tree has no batch record, so pass
  `--formals` and state where the list came from — the collision precheck's output, itself derived
  from the route's refusal message.
- **Build the variant into scratch, strip-check, then replace.** The script's contract is
  "a variant beside the original"; the customer migration is in-place, and the proof must run while
  both sides still exist.
- **fusion-tea's tree is dirty** on `item8-fusion-embedded-catalog` (6 ahead / 0 behind main). Clean
  or stash before branching, and say in the plan which was done.
- **Codegen's working tree carries uncommitted `dead-worktree-pins` edits.** They belong to another
  item; do not sweep them into this item's commits.
- The F-3 re-raise is roughly this shape:

```python
try:
    self._graph.validate()
except GraphValidationError as error:
    raise ElaborationDiagnosticError(error.diagnostics) from error
if self._strict and self._graph.diagnostics:
    raise ElaborationDiagnosticError(self._graph.diagnostics)
```

---

## Potential Risks

- **`.claude/` is unverified (B1's blind spot).** The 23-file tree was not readable this session and
  is not packaged. *Mitigation:* the plan's first act in agentic-mbse is the same two greps
  (`in (\w+)\s*=\s*\1\s*;` and `^\s*in\s+\w+\s*=`) across `.claude/`, and the rollout follows what
  they return rather than what this design assumed.
- **A rename collides (B3 false).** *Mitigation:* D5's precheck runs first and stops the run; and
  after D6, the failure it would have caused reports itself by name instead of as a traceback.
- **The customer library has drifted from the fixture (B2 false).** *Mitigation:* the collision
  precheck reads the customer tree, not the fixture, so a differing declaration set surfaces before
  any write. If the sets differ materially, stop and surface it — do not re-derive silently.
- **F-2 turns out not to be contained.** The disposition is explicit: stop and file it with a name,
  owner, and vehicle rather than growing the item. The same rule applies to F-3 if the located cause
  is wrong.
- **Where smell 7 could bite.** The product lens flagged forward: if the design settles on "the
  guidance teaches it" for a behavior the route cannot enforce, the loud-failure invariant has moved
  from the generator to the reader. The live case is F-4's sideways reach — it is silent and correct
  by the measured rule, and a second occurrence converts it to a loud refusal. D3 answers this
  directly: the sideways shape gets a tracked fixture and a conformance assertion, so the sentence in
  the guidance describes something CI holds, not something a reader must remember.

---

## Integration Strategy

The exact route is the only route; nothing here adds a stage or an option to it. The F-3 repair makes
an existing refusal report like every other refusal. The migration moves the customer model onto the
form the codegen fixture has used since the cutover, so the two stop diverging on binding form (they
still diverge on `hif_driver_instance`, which is R-2's business and stays that way per D8). The
guidance rewrite replaces a section that currently contradicts the shipped route; `plant-idiom.md`
already carries the "reference fixtures live in sysml-codegen under `tests/fixtures/`" convention,
so D3's provenance links extend an existing habit rather than inventing one.

---

## Validation Approach

**Spine — the mutation check** (the criterion that decides the item):
mutate `gain` off default in the migrated customer model, regenerate, and assert **every** — one
entry point keyed on the supplying attribute carries the new value and all three consumer modules
wire to it — and **only** — no other entry point value moves.

**Necessary evidence, not sufficient:**

- `generate`, `seal`, and `snapshot` on the migrated customer model, zero readiness diagnostics.
- Live and `--from-snapshot` packages byte-identical.

**Both paths refuse the self-named form:**

- codegen: `SI_SELF_BINDING`, exit 1, output directory empty, on a fixture that pins the shape.
- agentic-mbse: `validate_structure` returns `L2_SELF_NAMED_BINDING`, `success=False`.
- **and, post-F-2**, the D-6 form is accepted by both: codegen generates it, agentic-mbse no longer
  errors on it. This is what makes "confirmed to refuse" an honest claim about *what* it refuses.

**The teaching is falsifiable:**

- the four-example grep returns zero across both trees;
- each promoted D-6 fixture's conformance assertion passes by diagnostic name or entry-point value;
- the full codegen suite green with the license loaded (`uv run --extra dev pytest tests/`).

**The migration is bounded:** the strip check reports zero problems.

**Stellarator:** one run recorded — command, exit code, first refusal class and count, and a filed
follow-on. No fix, no reversal of the July hold.

---

## Next-Stage Handoff

**Fixed.** D-5 for all 15 fusion-tea sites. One authoritative copy (D1). No push, no PR. The R-2 pin
stays (D8). ADR-010 is filed decision-only (D9). Stellarator is triage-only (D10). Codegen fixtures
that pin the refused shape keep carrying it.

**Open, and the plan settles it with repo access.** The `.claude/` inventory and therefore the exact
file list for the rollout. Whether F-2 needs `binding.py` changed or only `level2_structure.py`.
Which scratch location the variant is built into.

**De-risk first, in this order.** (1) The collision precheck — it is license-free, it is the cheapest
step, and it is the one that can invalidate the mechanized migration. (2) The `.claude/` inventory —
it sizes the rollout. (3) The F-3 repair — it makes every later migration failure legible, so it
should land before the 15 renames run, not after.

**Surfaced, dependent conclusions parked.** The brief's migration site list omits the three
`models/library/analyses/` files that declare the 11 formals. Nothing upstream is falsified — D-5 has
always meant renaming the formal, `make_d5_variant.py` implements both halves, and the codegen
fixture proves the result — but the plan's file list must be six files, not three, and any downstream
estimate keyed to "15 sites in 3 files" is undersized.

---

## Appendix A — The 15 customer sites and their D-5 targets

From `reverted/fusion-tea-model-migration.patch` (authored lines) against
`tests/fixtures/fusion_tea/` (worked targets).

| file | line | authored | D-5 target |
|---|---|---|---|
| `designs/generic_ife/ife_plant.sysml` | 114 | `in availability = availability` | `in availability_in = availability` |
| | 116 | `in discount_rate = discount_rate` | `in discount_rate_in = discount_rate` |
| | 121 | `in frequency = frequency` | `in frequency_in = frequency` |
| | 122 | `in gain = gain` | `in gain_in = gain` |
| | 123 | `in om_cost_constant = om_cost_constant` | `in om_cost_constant_in = om_cost_constant` |
| | 124 | `in plant_cost_constant = plant_cost_constant` | `in plant_cost_constant_in = plant_cost_constant` |
| | 126 | `in thermal_efficiency = thermal_efficiency` | `in thermal_efficiency_in = thermal_efficiency` |
| | 146 | `in gain = gain` | `in gain_in = gain` |
| | 148 | `in thermal_efficiency = thermal_efficiency` | `in thermal_efficiency_in = thermal_efficiency` |
| | 168 | `in gain = gain` | `in gain_in = gain` |
| `designs/hif_ife/hif_driver.sysml` | 73 | `in beam_energy_mj = beam_energy_mj` | `in beam_energy_mj_in = beam_energy_mj` |
| | 75 | `in num_chambers = num_chambers` | `in num_chambers_in = num_chambers` |
| `designs/hif_ife/hif_plant.sysml` | 186 | `in thermal_power_gw = thermal_power_gw` | `in thermal_power_gw_in = thermal_power_gw` |
| | 215 | `in availability = availability` | `in availability_in = availability` |
| | 216 | `in net_electric_power_gw = net_electric_power_gw` | `in net_electric_power_gw_in = net_electric_power_gw` |

Declaration side — 11 distinct formals, three library files:
`ife_lcoe.sysml` (availability, discount_rate, frequency, gain, om_cost_constant,
plant_cost_constant, thermal_efficiency), `hif_economics.sysml` (beam_energy_mj, num_chambers,
thermal_power_gw, availability, net_electric_power_gw), `fusion_cycle.sysml` (gain,
thermal_efficiency — including a `constraint def` formal).

## Appendix B — Measured behavior the guidance is written from

Condensed from `spike/findings.md`; that file, not this table, is the authority.

| shape | position | outcome |
|---|---|---|
| `in availability = availability` | anywhere | refused, `SI_SELF_BINDING` (both paths) |
| `in availability_in = availability` | inside the def | generates; entry point on the outer attribute; mutation moves it |
| `in driver_cost = driver.cost` | any | generates; entry point on that occurrence's feature |
| `in availability = 'Plant'::availability` | inside the def, 1 or 2 occurrences | generates; each occurrence reads its own value |
| `in unit_cost = 'Unit'::cost` | inside the def, 2 leaf occurrences below | refused, `SI_OCCURRENCE_AMBIGUOUS` |
| `in availability = 'Plant'::availability` | above the def, 1 occurrence | generates |
| `in availability = 'Plant'::availability` | above the def, 2 occurrences | refused, `SI_OCCURRENCE_AMBIGUOUS` |
| `in unit_cost = 'Unit'::cost` | no local occurrence, 1 in a sibling subtree | generates — resolves sideways (F-4) |
| D-5 rename colliding with an `out` formal | — | traceback today; named diagnostic after D6 |
| D-5 rename colliding with a second `in` formal | — | `SI_OCCURRENCE_MISSING`, detail unreadable (filed) |

---

**Next Step:** After approval → `/_my_design_review`, then `/_my_plan`.
