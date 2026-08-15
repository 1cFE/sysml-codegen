# Design: Self-Binding Replacement — Establish, Document, Migrate

**Status:** Draft (rev 2 — rewritten against re-run discovery after `design-review.md`, verdict Revise)
**Owner:** Reid W
**Stage:** `design` (orchestrated run; briefs `04-design.md`, `05-design-revision.md`)
**Created:** 2026-08-15 · **Revised:** 2026-08-15 (rev 2)
**Repo state:** codegen `main` @ `7e95285`; working tree carries the uncommitted `dead-worktree-pins` edits
**Complexity:** MEDIUM

---

## Overview

Teach one situational rule for binding a modelled value into a calculation, hold it in exactly one
authoritative document, reach every surface that instructs a human or an agent, migrate the
fusion-tea self-bindings to the ratified D-5 form with a mechanical proof that only the referent
changed, and prove the value now arrives by mutation across every renamed formal.

## Related Artifacts

- **Spec:** `.project/active/self-binding-replacement/spec.md` (rev 3)
- **Measured authority:** `.project/active/self-binding-replacement/spike/findings.md`
  — plus the pending usage-qualified addendum (see D11)
- **Dispositions:** `.project/active/self-binding-replacement/briefs/03-spike-dispositions.md`
- **Align record:** `.project/active/self-binding-replacement/briefs/00-align.md`
- **Design review:** `.project/active/self-binding-replacement/design-review.md` — verdict Revise,
  six must-fix; resolutions in the Revision Record at the end of this document
- **Scope context:** `.project/research/20260815-103905_item8-bounded-stocktake.md`
- **Contract (D-4…D-7):** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:604-627`
- **Product lens:** `.project/active/self-binding-replacement/product-lens.md`

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

The owner restated the obligation on 2026-08-15 (`epic:71-78`), quoted in full because the bookends
are the scope limiter:

> "all I care about is: We know what the RIGHT pattern(s) are for the given situation / We document
> those right patterns / We fix the models to use the right patterns. `in R = R` is the wrong
> pattern. I would like to detect the use of it so we avoid it in the future. that's it, that's all
> I care about."

Four clauses, and the deliverable is all four. Generation and seal are necessary evidence, not the
goal. The goal is that the rule is known, written where humans and agents read it, applied to the
models, and the wrong form confirmed refused before generation.

---

## Research Findings

### Discovery was re-run, and the method is now stated once and reused

Rev 1 built its surface inventory from `^\s*in\s+\w+\s*=` — anchored to line start, bare word. The
review falsified it, and the falsification is reproduced here: over `plant-idiom.md` that pattern
returns 5 hits where the corrected pattern returns 16, and **the three it misses include line 79** —
one of the four refused examples this whole item exists to correct. A pattern that cannot see the
defect it is auditing for is not an audit.

**The inventory pattern, validated against known positives before use:**

| purpose | pattern |
|---|---|
| any calculation-input binding | `\bin\s+[\w']+\s*=` |
| self-named binding (worked example) | `\bin\s+([\w']+)\s*=\s*\1\s*[;}]` |
| owner-qualified binding | `\bin\s+[\w']+\s*=\s*[^;=]*::` |

The single-quote class matters: SysML names are frequently quoted (`'HIF Driver'::x`), and `\w`
alone drops them. Each pattern was checked against `plant-idiom.md:79` (single-line, brace-enclosed)
and `:84-85` (indented) before being run at scale.

**Scope of the re-run:** `claude/` (5 agents, 15 commands, 10 skills), `docs/patterns/` (16 docs),
and **`project_templates/`** — the tree rev 1 missed entirely, which seeds every new project's
guidance. The stdlib and specification dumps under `docs/sysmlv2/` are excluded as upstream
reference material, not guidance this project authors.

### The corrected inventory

Binding examples per surface, corrected pattern:

| tree | file | count |
|---|---|---|
| `docs/patterns/` | `plant-idiom.md` | 16 |
| | `expose-pattern.md` | 15 |
| | `cross-file-binding.md` | 15 |
| | `syntax-reference.md`, `common-mistakes.md`, `constraints.md` | 4 each |
| | `adr002-calculations.md` | 3 |
| | `semantic-operators.md` | 2 |
| `claude/` | `skills/sysml-conventions/SKILL.md` | **7** (rev 1 said 4) |
| | every other file — 5 agents, 15 commands, 9 other skills | 0 |
| `project_templates/` | `MODELING_PROCESS.md.template` | **3** (rev 1: absent) |
| | `MODELING_GUIDE.md.template` | **1** (rev 1: absent) |

**What survived the corrected pattern, and it matters:** the self-named audit is unchanged. Exactly
four worked `in x = x` examples exist across all three trees, all in `plant-idiom.md` at `:79`,
`:84`, `:85`, `:200`, with deliberate prose negatives at `:40`, `:42`, `:46`. Rev 1's central
finding about the refused form was right; only the wider inventory around it was wrong.

**What did not survive:** rev 1's conclusion that the guidance edit is "a bounded edit, not a sweep"
was drawn from auditing one of the three forms. The rule being published governs three, and the
owner-qualified form is taught **13 times across 5 files with no statement of the position rule
anywhere**:

| file | lines | qualifier |
|---|---|---|
| `expose-pattern.md` | 19, 20, 66, 67, 118, 119 | `geometry::`, `producer_part::`, `geometry_module::` |
| `cross-file-binding.md` | 60, 61 | `geometry_module::` |
| `adr002-calculations.md` | 106, 107 | `component::` |
| `syntax-reference.md` | 93 | `my_component::` |
| `project_templates/MODELING_PROCESS.md.template` | 349, 350 | `my_component::` |

Three further sites (`syntax-reference.md:308`, `cross-file-binding.md:198`,
`common-mistakes.md:309`) already teach a qualified form as a **negative** ("Won't resolve!") and
need no correction.

### All 13 qualified examples are one shape, and it is the shape nobody measured

Reading the enclosing context of every one of the 13: each sits inside `part <usage> { ... }` and
qualifies by **that enclosing usage's own name** —

```sysml
part geometry {
    calc dimension_calc : DimensionCalculation {
        in length = geometry::input_length;   // qualifier = the enclosing part USAGE
    }
}
```

The spike measured **definition**-qualified references throughout: `'Plant'::availability`,
`'Unit'::cost` (`findings.md` rows 4a–4e, 6). Not one measured row used a usage qualifier. The
spec's own Change Record flags the distinction as live: *"The SysML action example's qualifier points
toward an enclosing usage name, not the definition-qualified spelling used by ten sites in the
reverted migration"* (`spec.md:218-219`).

⚠ **Surfaced, dependent conclusion parked.** Whether the measured position rule covers the
usage-qualified spelling is **unknown**. It is uniform across all 13 sites, so one measurement
settles all of them, and the orchestrator has the spike re-running now. Until that addendum lands,
this design states what it will teach under each outcome and publishes neither (D11).

One site deserves separate note because it is the most consequential in the tree:
`MODELING_PROCESS.md.template:349` is `in volume = my_component::volume` — a qualifier used
specifically to resolve a self-name collision. The project template that seeds every new project
teaches an **unmeasured spelling as the fix for the exact defect this item exists to end**.

### The migration target is already worked, in this repo

`tests/fixtures/fusion_tea/` is the customer model already D-5 migrated: **11 distinct formals across
15 declaration lines in 5 definitions in 3 library files**, plus 15 usage binding left sides in 3
design files.

| library file | declaration lines | formals |
|---|---|---|
| `library/analyses/ife_lcoe.sysml` | 31, 33, 38, 39, 40, 41, 43 | availability, discount_rate, frequency, gain, om_cost_constant, plant_cost_constant, thermal_efficiency |
| `library/analyses/hif_economics.sysml` | 25, 27, 57, 100, 101 | beam_energy_mj, num_chambers, thermal_power_gw, availability, net_electric_power_gw |
| `library/analyses/fusion_cycle.sysml` | 20, 22, 47 (a `constraint def` formal) | gain, thermal_efficiency |

`availability`, `gain` and `thermal_efficiency` each appear in **two** definitions, so 11 names is
not 11 edits. The plan counts declaration lines, not names.

⚠ **Scope correction, carried forward from rev 1 and still standing.** The brief's site list names
only the three design files. D-5 renames the *formal*, so the declaring `calc def` / `constraint def`
must be edited too. `make_d5_variant.py:203-229` implements both halves and the fixture proves the
result elaborates. Nothing upstream is falsified; the enumeration grows.

### The customer repo keeps a second synced model tree

This repo's own record: *"Deleted `part hif_driver_instance` from BOTH
`models/designs/hif_ife/hif_driver.sysml` and the `exploration/ife_e2e/models/` copy **(kept in
sync)**"* (`.project/active/fusiontea-acceptance/plan.md:365-368`). The reverted patch touched
`models/` only, so it does not settle whether that copy still carries self-bindings. Neither this
session nor rev 1's could read the customer tree. That is precisely why the site list must be a
discovery step at plan time rather than a path list at design time (D12).

### The spine's mutation site was wrong in rev 1

`designs/generic_ife/ife_plant.sysml` declares `part def 'IFE Power Plant'` at `:7` and **no usage**.
It mints no occurrence, no module, and no entry point — confirmed against the authored oracle
(`test_projection_wiring_contract.py`, 27 keys, none `ife_plant`-prefixed). Rev 1 told an implementer
to mutate a value in a file that has none.

The mutation site is `designs/hif_ife/hif_plant.sysml:87` — `:>> gain = 80.0`, under
`part hif_plant : 'IFE Power Plant'` at `:8`. It mints `hif_plant_pkg__hif_plant__gain`,
`DESIGN_ATTRIBUTE` (oracle `:60`).

And `gain`'s three consumers in `ife_plant.sysml` are **not three calc modules**: `lcoe_calc` (`:98`,
binding at `:122`), `recirc_calc` (`:134`, binding at `:146`), and `assert constraint viability :
'Viability Threshold'` (`:155`, binding at `:168`). The constraint is a real consumer and a real
published module — `_regular_inputs` accepts `CalcNode | ConstraintNode`
(`elaboration/project.py:503-539`), `_build_constraint_modules` (`:845`) emits it, and it publishes
as `hif_plant_pkg__hif_plant__viability__81ddf10fb1d1749b__evaluation`
(`test_fusion_tea_real_teax.py:68`).

### The authored oracle already enumerates all 11 supplying attributes

`test_projection_wiring_contract.py:41-66` lists every one of the 11 renamed formals' supplying
attributes as a `DESIGN_ATTRIBUTE` entry point: nine keyed `hif_plant_pkg__hif_plant__*`
(availability, discount_rate, frequency, gain, net_electric_power_gw, om_cost_constant,
plant_cost_constant, thermal_efficiency, thermal_power_gw), two keyed
`hif_plant_pkg__hif_plant__driver__*` (beam_energy_mj, num_chambers), and two fixture-only
`hif_driver__hif_driver_instance__*` copies that the customer repo deleted in July as R-2.

This turns the widened spine (MF-7) from a proposal into a mechanical enumeration with a known
expected answer.

### The migration tool does more than rename

`build_variant` calls `apply_aggregation_split(text)` unconditionally
(`scripts/make_d5_variant.py:224`), which introduces named intermediate attributes and restructures a
rollup expression (`:153-187`). `strip_check` computes the rewrites from the source and undoes them
from the variant **before** the byte comparison (`:261-262`). By construction the strip check cannot
see an aggregation split. The repo says so: *"A shape change cannot be proved by stripping a
suffix"* (`tests/conformance/test_d5_variants.py:174-179`).

Measured: zero rollup matches in `tests/fixtures/fusion_tea`, so the split does not fire there. The
risk is **latent, not active** — and the customer tree is unread.

### Prior decisions consulted

`.project/adr/INDEX.md` does not exist. Per `CLAUDE.md` an ADR is a numbered section of
`docs/architecture/modeling-assumptions.md`; nine exist, next free id ADR-010, and ADR-009 (`:704`)
carries the `(ADR-0NN)` title suffix that sections 1–8 predate. No ADR covers binding resolution, and
the Validation Rules table (`:747-762`) lists V1–V11 without mentioning `SI_SELF_BINDING`.

---

## Core Concept

**One rule, one copy, three legs of machine-owned enforcement.**

The rule is situational and short: *a calculation input binds to the modelled value you name, and the
name is resolved from where the consumer sits.* Three situations follow from where the value lives.
The value is an attribute on the part owning the calculation → make the two names differ and bind
bare (D-5). The value lives on another part → name the occurrence path (D-7). You reach by owner
qualification (D-6) → it resolves by position, in two steps the spike wrote down:

1. Walk the consumer's own scope lineage outward. If any scope in that lineage owns the slot, that
   occurrence wins — however many other occurrences exist elsewhere.
2. Only if the lineage misses, search descendants of each lineage anchor, innermost first. One
   match is selected silently; two collide and refuse as `SI_OCCURRENCE_AMBIGUOUS`.

Step 2 is why owner qualification reaches *sideways* into a sibling subtree when exactly one
occurrence lives there. Owner qualification does not mean "mine."

That rule lives in exactly one document, `agentic-mbse/docs/patterns/plant-idiom.md`, reorganized by
situation. Everything else points at it. The two-copies trap that Item 7 left as residual A-1 is not
fought by synchronizing copies; it is dissolved by there being one copy to reach.

Three legs then keep the rule honest, and each is owned by a machine rather than a reader:

1. **The generator refuses the wrong form** — already shipped (`SI_SELF_BINDING`), confirmed on both
   paths, not rebuilt.
2. **Every published example is provenance-linked to a tracked fixture the shipped route actually
   elaborates or refuses, and a conformance test compares the doc text to the fixture text** — so
   "parser-validated" is a gate rather than an author's care, which is what failed last time.
3. **The migration's proof is a strip check with its blind spot closed by an explicit guard** — undo
   the renames and the original must return byte for byte, and the run refuses to start if the
   tool's second transformation would fire.

Why this is right and not merely workable: the failure this item exists to end is *a document that
teaches what the product refuses*. Any design that keeps the teaching in more than one place, or that
validates examples by reading them, reproduces that failure in a new spot. The corrected inventory
strengthened this rather than weakening it — finding four more instruction surfaces is an argument
for fewer copies, not more.

---

## Key Bets

- **B1.** The packaged `agentic_mbse_data` tree was byte-identical to the agentic-mbse working tree
  **as of install, 2026-08-15 08:17** (hardlink, link count 2, mtime `1786807058`, re-verified this
  session on `plant-idiom.md`, the skill, and `expose-pattern.md`). *If false, or if the link is
  later broken by a checkout or an editor that writes a new inode → every surface measurement in this
  document is stale.* This is point-in-time evidence, not a standing property: implement re-checks
  the link counts as its first act and re-runs the three patterns over the **whole** agentic-mbse
  tree, not just `.claude/`.
- **B2.** The customer `fusion-tea` library definitions are the same definitions as
  `tests/fixtures/fusion_tea/library/analyses/*.sysml`, so the fixture is the worked target for the
  same sites. *If false → the 11-name / 15-line rename set is wrong and must be re-derived from the
  customer tree before anything is written.* Independently supported: all 15 customer binding lines
  in the reverted patch sit at the same line numbers as the fixture's.
- **B3.** No definition involved in the migration declares a second member with the same bare name as
  a renamed formal (an `out`, or a second `in`). *If false → after the rename the bare right-hand
  side lands on that sibling formal, producing spike row 5's cycle or row 7's
  `SI_OCCURRENCE_MISSING`, and that site needs D-7 instead of D-5.*
- **B4.** The measured resolution rule is the behavior of the route at the commit this item lands on.
  *If false → the guidance teaches a rule the shipped route does not implement.*
- **B5.** A `DESIGN_ATTRIBUTE` entry point keys by the supplying attribute's display path, so N
  consumers of one modelled value share one key. *If false → the "every and only" check cannot be
  read off the entry-point set.* Confirmed against the authored oracle.
- **B6.** *(was hidden — H1)* The migration tool's only edit on the customer tree is the rename.
  *If false → `apply_aggregation_split` restructures a rollup expression and the strip check, which
  undoes aggregation rewrites before comparing, cannot see it — a silent physics change inside a
  "bounded diff".* Closed by an explicit guard, not by hope (D5).
- **B7.** *(was hidden — H2)* Every `in <name> =` left side in the six files belongs to a usage typed
  to a definition whose formal is being renamed. *If false → `_rename_binding_left_sides` rewrites
  file-wide and silently breaks a usage of a different calc def that happens to declare a same-named
  formal.* Eleven names across six files is enough surface for this to bite.
- **B8.** *(was hidden — H3)* The customer model's binding sites live only under `models/`. *If false
  → `exploration/ife_e2e/models/` is left behind and the two synced trees drift on binding form.*
  This repo's own record says the copy exists (`fusiontea-acceptance/plan.md:365-368`), so B8 is
  treated as probably false and answered by discovery (D12).

## Key Decisions

- **D1. One authoritative copy: `agentic-mbse/docs/patterns/plant-idiom.md`, reorganized by
  situation.** Every other surface carries a pointer plus, at most, the one-paragraph rule.
  *Rejected: replicate the full rule into each surface* — that is the divergence the Item-7 A-1
  residual already produced, and the corrected inventory found the drift already present:
  `MODELING_GUIDE.md.template:145` and `sysml-conventions/SKILL.md:210` carry the same binding
  example verbatim. **The corrected inventory did not overturn this conclusion — it widened the
  pointer list from 1 surface to 3 and strengthened the argument for one copy.**
- **D2. Three surfaces carry the rule inline, briefly, as well as the pointer:**
  `claude/skills/sysml-conventions/SKILL.md`, `project_templates/MODELING_PROCESS.md.template`, and
  `project_templates/MODELING_GUIDE.md.template`. One Common-Pitfalls row, one short subsection
  naming the three situations, one reference line each. *Rejected: pointer only* — the skill is what
  loads when an agent writes SysML and the templates are what a new project starts from; neither
  reader has a reason to go look. *Rejected: full teaching inline* — that mints three more copies.
- **D3. Examples are validated by fixture provenance plus a drift-check conformance test.** Every
  taught shape cites a tracked codegen fixture whose exact-route outcome a conformance test pins,
  **and** a codegen test reads the packaged `agentic_mbse_data/docs/patterns/plant-idiom.md`,
  extracts each fenced block carrying a provenance marker, and asserts verbatim containment in the
  cited fixture file. *Rejected: provenance citation alone (rev 1)* — a citation is a pointer, not a
  comparison, and nothing failed when doc and fixture drifted in either direction. *Rejected: parse
  each fenced snippet* — parsing proves the fragment is legal SysML, which is exactly what the four
  refused examples already are.
- **D4. The migration is mechanized by `scripts/make_d5_variant.py`, extended with a `--root`.**
  Build into a scratch directory, strip-check against the customer originals, then replace.
  *Rejected: hand edits reviewed as a diff* — B3's collision family and a stray reformat are what a
  large diff hides. *Rejected: rewrite in place then check* — nothing left to compare against.
- **D5. Four preconditions gate the run, all license-free, all over model text.** Per renamed formal:
  (a) does its declaring definition still declare a member of that bare name after the rename;
  (b) does it already declare `<name>_in`; (c) **B7** — does any `in <name> =` left side in scope
  belong to a usage typed to a definition whose formal is *not* being renamed; (d) **B6** — does
  `aggregation_rewrites()` return anything for any customer file. Any yes stops the run.
  *Rejected: discover these by running the route* — (a)–(c) surface as spike row 5's cycle, whose
  current report names nothing, and (d) does not surface at all.
- **D6. F-3 is fixed in codegen, in two contained places.** Wrap `elaborate.py:631` so
  `GraphValidationError` becomes `ElaborationDiagnosticError`, and make `_validate_producer_cycles`
  report the participants. **Sized honestly:** the traversal changes shape — `visit()` is a boolean
  DFS whose `complete` memo returns `False` for an already-visited node and which discards the active
  stack, so producing a participant set means retaining the stack at closure or switching to SCC
  detection (`graph.py:862-892`). Still one method, so the disposition's "file it if it needs
  graph-layer restructuring" bar is not met — but the plan budgets for a traversal change, not a
  payload tweak, and covers it with a test on the `s5_sibling_formal` shape. *Rejected: filing it.*
- **D7. F-2 is fixed in agentic-mbse only**, by comparing the referent element of the member's
  `feature_value_expression` to the member itself instead of comparing `binding.source_path` to
  `binding.param_name` (`level2_structure.py:350`). *Rejected: special-casing qualified spellings by
  string* — the same name-based class of check that produced the false positive.
- **D8. The `hif_driver_instance` / R-2 acceptance pin is left exactly as it is.** *Rejected:
  re-anchoring it here.* The pin's subject is `tests/fixtures/fusion_tea`, which still declares
  `part hif_driver_instance` at `designs/hif_ife/hif_driver.sysml:100`, is already D-5, and is not a
  migration target. The 9-vs-11 channel question belongs to the customer-repo regeneration remainder,
  an explicit Non-Goal. Smaller call, does not contradict R-2. *(Verified independently by review.)*
- **D9. ADR-010 is filed** as `## 10. Calculation Input Bindings Resolve by Identity, Not by Name
  (ADR-010)` in `docs/architecture/modeling-assumptions.md`, decision-and-consequence only, naming
  plant-idiom.md as the one home for worked examples, **and the Validation Rules table gains a row
  for `SI_SELF_BINDING`** — a reader asking "which rule refuses this?" reads that table.
  *Rejected: not filing it* — the refusal is a shipped behavior constraining every customer model and
  no ADR or validation row covers it. *Rejected: putting the teaching text in the ADR* — second copy.
- **D10. Stellarator gets one pipeline run, a written record, and a filed follow-on. Nothing is
  fixed.** *Rejected: migrating its 15 copied-in fusion-tea files while we are in there* — the July
  owner hold is not reversed by this item.
- **D11. *(new)* The D-6 section is parameterised on the pending spike addendum, and neither branch
  is published before it lands.** All 13 published qualified examples use one uniform spelling —
  qualification by the enclosing part **usage** — which the spike never measured. Two outcomes, both
  pre-decided so the addendum lands as a fact rather than a new decision:
  - **If the position rule holds for the usage qualifier too:** the D-6 section teaches one rule for
    both spellings, and the 13 sites each gain a one-line position caveat with a pointer. No
    rewrites.
  - **If the qualifier kind alters the resolution path:** the D-6 section teaches the two spellings
    separately with their measured behaviors, `MODELING_PROCESS.md.template:349-350` is **rewritten**
    rather than caveated — it teaches the qualifier as a self-collision fix and would be teaching a
    wrong one — and any spelling still unmeasured is stated as unmeasured rather than given a rule.
  *Rejected: publishing the definition-qualified rule as if it covered both* — that is the exact
  defect this item exists to end, one level up.
- **D12. *(new)* The migration site list is produced by discovery over the whole customer repo, not
  by the path list in this design.** Two greps — the self-named pattern, and a declaration-side
  search for the 11 formals — run over `/home/reid/1cfe/fusion-tea` including
  `exploration/ife_e2e/models/`. The six files are the **expected result**, not the definition, and
  what the greps return is recorded. *Rejected: the fixed six-file list* — this repo records a second
  synced model tree, neither this session nor rev 1's could read the customer repo, and rev 1's own
  headline finding was that an assumed list was undersized.

---

## Architecture

### Where each change lands

| repo | change |
|---|---|
| **agentic-mbse** | `docs/patterns/plant-idiom.md` rewritten by situation, four refused examples corrected; **the 13 qualified sites across `expose-pattern.md`, `cross-file-binding.md`, `adr002-calculations.md`, `syntax-reference.md`, `MODELING_PROCESS.md.template` caveated or rewritten per D11**; `claude/skills/sysml-conventions/SKILL.md`, `project_templates/MODELING_PROCESS.md.template`, `project_templates/MODELING_GUIDE.md.template` gain the rule + pointer; `.claude/`'s counterparts per the inventory; F-2 identity comparison in `validation/level2_structure.py` (+ `binding.py` if the referent must be exposed) with a test per direction |
| **sysml-codegen** (here) | F-3 repair in `elaboration/elaborate.py` and `elaboration/graph.py` + tests; three promoted D-6 fixtures + one conformance test; the D3 doc-drift conformance test; `scripts/make_d5_variant.py` gains `--root` and the aggregation guard (docstring updated — its "originals are never touched" contract is inverted by D4); ADR-010 + product-ledger row + the `SI_SELF_BINDING` validation-rule row; the stellarator triage record |
| **fusion-tea** | whatever D12's discovery returns — expected: 3 design files (15 binding left sides) + 3 library files (15 declaration lines, 5 definitions), plus any `exploration/ife_e2e/models/` copy, on a branch off `item8-fusion-embedded-catalog` |
| **fusion-tea-stellarator-mbse-demo** | nothing. One run, recorded in codegen. |

Local commits only in every repo. No push, no PR (`briefs/00-align.md`).

**Which agent tree is authoritative.** Codegen's `.claude/agents/*.md` and
`.claude/skills/sysml-conventions` are symlinks into `agentic-mbse/claude/`, not into `.claude/`. So
D2's edit to `claude/skills/sysml-conventions/SKILL.md` reaches this repo's agents automatically,
and `claude/` is the tree to treat as authoritative. `.claude/` remains unread from this sandbox; the
plan inventories it and records whether its pointer is duplicated deliberately or generated from
`claude/`. Until that is settled the pointer is duplicated by hand in two trees — a smaller version
of the same trap, named rather than hidden.

### The teaching, organized by situation

The rewritten self-binding section answers one question — *where does the value live?* — and hands
back one form:

1. **On the part that owns the calculation → D-5.** Rename the calculation's input and bind bare:
   `in availability_in = availability`. Pinned by `tests/fixtures/fusion_tea` (spike row 2; mutation
   proved at row 2m).
2. **On a different part → D-7.** Name the occurrence path: `in driver_cost = driver.cost`. Pinned by
   `tests/fixtures/fusion_tea` (`in driver_cost_constant = driver.cost_per_joule`; spike row 3).
3. **By owner qualification → D-6, with the two-step position rule stated as two steps**, and its
   sideways reach called out. Definition-qualified behavior is measured (rows 4a–4e, 6);
   usage-qualified behavior is pending and governed by D11.

Plus the negative, kept and sharpened: `in x = x` binds the calculation's input to itself, is refused
by both paths, and is never reinterpreted as an outer reference (D-4, `[OWNER-VERBATIM]`).

Two authority corrections travel with the rewrite: SysML v2 Part 1 §7.17.2 is **not** cited as
authority for a shadowing rule, and the `:>>` explanation cites KerML §7.3.4.5 for "the owner's own
namespace excluded", with §8.2.3.5.1 as the abstract-syntax mechanism.

### The migration, as a pipeline with a proof in the middle

```
D12 discovery over the whole customer repo → the actual site list
      ↓
D5 preconditions (a)-(d), license-free, text only
      ↓  stops on a sibling-formal collision, a file-wide rename hazard, or a live rollup
build variant into scratch  (make_d5_variant --root <fusion-tea>)
      ↓
strip check: remove `_in` everywhere → must reproduce the originals byte for byte
      ↓  any mismatch = something other than the rename happened; stop
replace originals, commit on a branch off item8-fusion-embedded-catalog
      ↓
generate + seal + snapshot, zero readiness diagnostics
      ↓
spine: enumerate all 11 entry points, then two off-default mutations
```

The strip check is the bounded-diff mechanism, and its limit is now written down rather than assumed:
it proves *the rename was the only suffix-shaped edit*. It cannot see the tool's aggregation split,
because `strip_check` undoes those rewrites before comparing. D5(d) closes that by refusing to run at
all when a rollup would match, so the check's guarantee and the tool's behavior coincide.

---

## The Spine

The criterion that decides the item, specified concretely because it is the step that decides it.

**Mutation site.** `designs/hif_ife/hif_plant.sysml:87` — `:>> gain = 80.0`, under
`part hif_plant : 'IFE Power Plant'` (`:8`). **Not** `ife_plant.sysml`, which declares only a
`part def`, mints no occurrence, and has no value to mutate.

**Expected key.** `hif_plant_pkg__hif_plant__gain`, `DESIGN_ATTRIBUTE`.

**The three consumers, named individually because one is not a calc:**

| consumer | declared | binding | module |
|---|---|---|---|
| `lcoe_calc` | `ife_plant.sysml:98` | `:122` | calc module |
| `recirc_calc` | `ife_plant.sysml:134` | `:146` | calc module |
| `assert constraint viability : 'Viability Threshold'` | `ife_plant.sysml:155` | `:168` | **constraint module**, published as `…__viability__81ddf10fb1d1749b__evaluation` |

The constraint consumer additionally carries `formal_identity` (`project.py:543`) that the calc
consumers do not. "All three consumer modules" written flat is easy to implement as "the three calc
modules", silently dropping the one consumer class where every-and-only has historically been
hardest. It is enumerated here so it cannot be.

**Every and only, in three assertions:**

1. **Enumeration (all 11 formals).** After the one planned regeneration, assert that every one of the
   11 renamed formals' supplying attributes appears as a `DESIGN_ATTRIBUTE` entry point keyed on its
   display path. The expected set is the authored oracle's, minus the two
   `hif_driver__hif_driver_instance__*` keys the customer deleted in July. This is B5 applied as an
   enumeration rather than a spot check, and it costs no extra run.
2. **Arrival, plant-level.** Mutate `gain` off default; the one key carries the new value, and all
   three consumers above — two calc modules and the constraint module — wire to it. No other entry
   point's value moves.
3. **Arrival, child-level.** Mutate `beam_energy_mj` under the `part :>> driver` block; the key
   `hif_plant_pkg__hif_plant__driver__beam_energy_mj` carries the new value and its consumers wire to
   it. This exercises a different occurrence depth from assertion 2.

**Where this design disagrees with the review, and why.** MF-7's prescription was "add one off-default
mutation in a **second design file** so `hif_plant.sysml` carries an arrival check". That framing does
not fit this model: `ife_plant.sysml` and `hif_driver.sysml` both declare definitions, not usages, so
**every** design-attribute entry point roots at the single `hif_plant` usage. There is no second design
file to mutate in. The finding is accepted in full — one formal of eleven was not enough — but the
widening is by **formal and occurrence depth**, not by file. Assertion 1 covers all 11; assertions 2
and 3 cover two different depths. The residual failure mode MF-7 names — a renamed formal whose bare
right-hand side resolves to a same-named attribute in an *enclosing* scope, silently — is caught by
assertion 1, because such a formal would key its entry point somewhere other than its intended
supplying attribute's display path.

This is read off shipped public artifacts (`inputs/*.json`, `pipelines/pipeline.yaml`) and does not
require TEAx execution, which is what the spike established as sufficient at row 2m.

---

## Required Invariants

1. **One authoritative teaching copy.** Exactly one document states the situational rule in full;
   every other live surface either points at it or carries a pointer plus the one-paragraph summary.
2. **Zero unmarked self-named examples.** `grep -P "\bin\s+([\w']+)\s*=\s*\1\s*[;}]"` returns nothing
   across both trees except sites carrying an explicit refused-by-design marker. **This constrains
   how the counterexample may be written**: today's negatives at `plant-idiom.md:40,42,46` pass
   because they are prose, and the semicolon is what separates a worked example from a warning. A
   later author who sharpens the warning into a fenced code block breaks the gate unless they add the
   marker. Stated so that is a choice, not an accident.
3. **Every taught shape is either pinned by a tracked fixture, or explicitly labelled as taught on
   measurement without a fixture.** *(Narrowed from rev 1, which claimed all were pinned.)* Pinned:
   plain D-5, D-7, and three D-6 positions. **Not pinned, and labelled:** the inherited-attribute
   D-5 case (`plant-idiom.md:85`), the EXPOSE + D-5 case (`:200`), the attribute-rename D-5 spelling
   (`:59-61`, "as `wi014_toy` does"), and the usage-qualified D-6 spelling pending D11. The invariant
   must not claim more than CI holds — that is the failure mode this item exists to end.
4. **The migration's only edit is the rename, and the check that proves it is scoped to what it can
   see.** Stripping `_in` reproduces the originals byte for byte. The strip check does **not** cover
   the tool's aggregation split; D5(d) guarantees no split can fire by refusing to run when a rollup
   matches. Restated from rev 1, which asserted a guarantee the tool does not provide.
5. **The refused shape stays pinned.** `tests/fixtures/self_named_binding_trap`, `self_named_rescue`,
   and every fixture that exists to prove refusal keeps carrying `in x = x`.
6. **No readiness diagnostic escapes as a traceback**, and an internal invariant failure stays
   distinguishable from an authored-model refusal (see Implementation Notes).
7. **Both validation paths agree on the self-named form**, and after F-2 on D-6 as well.
   **Owner named:** codegen's `extraction/source_evidence.py:130-138` owns the rule; agentic-mbse's
   `level2_structure.py` mirrors it. **Nothing currently catches drift between them** — no test in
   either repo compares the two, merging them is out of scope, and this is stated plainly rather than
   asserted as an invariant something enforces.

---

## Component Overview

**agentic-mbse**

- `docs/patterns/plant-idiom.md` — the authoritative copy. Self-binding section reorganized by
  situation; the four refused examples at `:79`, `:84`, `:85`, `:200` corrected; the position rule
  written as two steps; F-4's sideways reach given its sentence.
- The 13 qualified sites (table in Research Findings) — caveated or rewritten per D11.
- `claude/skills/sysml-conventions/SKILL.md` — one Common-Pitfalls row, one short subsection, one
  reference line. Note `:210` duplicates `MODELING_GUIDE.md.template:145` verbatim.
- `project_templates/MODELING_PROCESS.md.template`, `MODELING_GUIDE.md.template` — same treatment;
  `MODELING_PROCESS.md.template:349-350` is the highest-priority site in the tree.
- `.claude/` counterparts — inventory first, then the same treatment.
- `validation/level2_structure.py::check_self_named_bindings` (+ `binding.py`) — D7, one test per
  direction.

**sysml-codegen (here)**

- `elaboration/elaborate.py:631` — guard the `validate()` call.
- `elaboration/graph.py::_validate_producer_cycles` — retain the traversal stack at closure and
  report the participants.
- `tests/fixtures/` — three promoted spike fixtures pinning D-6, each with a `PROVENANCE.md`:
  inside-the-def two-occurrence (generates, spike `s4b`), above-the-def two-occurrence (refused,
  `s8`), sideways reach (`s6`). None declares a constraint, so no expectation-file obligation
  attaches (`test_constraint_population_oracle.py:81-110`).
- One conformance test for those fixtures; one for D3's doc-drift check.
- `scripts/make_d5_variant.py` — `--root`, the D5(d) aggregation guard, docstring corrected.
- `docs/architecture/modeling-assumptions.md` — ADR-010 + the `SI_SELF_BINDING` validation row; the
  back-registered row in `.project/product/INDEX.md`.
- `.project/active/self-binding-replacement/stellarator-triage.md`.

**fusion-tea** — per D12's discovery; expected six files plus any `exploration/ife_e2e/models/` copy.

---

## Non-Goals

- **Reopening D-4.** It is `[OWNER-VERBATIM]` (2026-08-05) and settled: a self-binding is never
  reinterpreted as an outer reference.
- **Re-deriving the D-5 choice for the fusion-tea sites within this item.** This is a *decision*, not
  a settled rule: D-5/D-6/D-7 are `[AGENT] (ratified by owner, 2026-08-05)` and remain challengeable
  by re-deriving against their recorded reasoning. The reasoning that stands: D-5 needs no qualifier,
  scales to repeated subsystems, is what the shipped codegen fixture uses, and matches the owner's
  situational rule for an attribute on the part owning the calculation. D-6 turning out safer than
  the spec assumed does not by itself overturn that reasoning. *(Split from rev 1, which wrote this
  as a prohibition — the "WE MUST NOT ⟨suggestion⟩" shape capture-fidelity §3 names.)*
- The rest of Item 8: the July IFE impact audit, certification repair, the composed proof thread, the
  fourteen-document rewrite list.
- The regeneration remainder — package/contract regeneration on the customer repo, duplicate-field
  workaround removal, study lineage, acceptance-pin re-anchoring. Homed to
  `.project/active/elaborator-downstream/`, deliberately not created here.
- Migrating or repairing stellarator, including its 15 copied-in fusion-tea files.
- Building any new detector, lint, or authoring-time check.
- Merging the two self-binding checks into one implementation (Invariant 7).
- The second half of F-3 (`SI_OCCURRENCE_MISSING`'s bare `FeatureSlotId`) and F-5 (chain source
  paths). Both filed, not fixed.
- Any change to arithmetic, physical values, or model physics.

---

## Implementation Notes

- **Do not edit through the venv path.** `agentic_mbse_data/...` files are hardlinks to the
  agentic-mbse source. An in-place editor would silently mutate the source repo; one that writes a
  new file breaks the link and leaves a stale package. Read there, write in `/home/reid/1cfe/agentic-mbse/`.
  The D3 drift test reads that snapshot and must fail loudly if the link count is not 2.
- **Re-verify B1 first.** Check link counts, then re-run the three patterns over the whole
  agentic-mbse tree. Everything in Research Findings is point-in-time.
- **The license is required** for generate/seal/snapshot:
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. A green run without it is not a run.
- **`make_d5_variant.py` needs `--formals` supplied** for a tree with no batch record, with a stated
  source — D5's precheck output.
- **Build into scratch, strip-check, then replace.** The script's contract is "a variant beside the
  original"; the customer migration is in-place and the proof must run while both sides exist.
- **fusion-tea's tree is dirty** on `item8-fusion-embedded-catalog` (6 ahead / 0 behind main). Clean
  or stash first, and record which.
- **Codegen's working tree carries uncommitted `dead-worktree-pins` edits.** Another item's; do not
  sweep them in.
- **The F-3 re-raise widens what reads as a model refusal.** `validate()` raises on the whole failure
  set, and most of `graph.py:400-448` checks codegen's own referential integrity, not authored model
  shape. After the change a codegen bug surfaces as "Model failed exact-route validation" with exit 1
  — indistinguishable from a bad model. Keep the two apart: the cycle diagnostic carries the offending
  binding and its participants, and internal-integrity diagnostics keep the `<instance-graph>`
  consumer display they already have, so the message says which kind of failure it is. Sizing
  decision, recorded, not a redesign.

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

- **B1 is point-in-time.** *Mitigation:* re-verify link counts and re-run all three patterns over the
  whole tree as implement's first act — not just `.claude/`, and not just the self-named pattern.
- **`.claude/` remains unread.** 23 files, 4 skills, unpackaged and unreachable from this sandbox.
  *Mitigation:* it is D12's sibling — an inventory step at plan time, with the corrected patterns, and
  the rollout follows what it returns.
- **The usage-qualified spelling may behave differently (D11).** *Mitigation:* nothing is published
  for it until measured; both branches are pre-decided so the addendum lands as a fact.
- **A rename collides, or the file-wide rewrite over-reaches (B3, B7).** *Mitigation:* D5(a)–(c) stop
  the run; and after D6 the failure that would follow reports itself by name instead of as a traceback.
- **The customer tree has drifted from the fixture (B2), or has sites the six-file list misses (B8).**
  *Mitigation:* D12 discovers rather than assumes. If the discovered set differs materially from the
  expected six, stop and surface it.
- **F-2 or F-3 turns out not to be contained.** The disposition is explicit: stop and file with a
  name, owner, and vehicle rather than growing the item.
- **Where the reader still owns something.** A fixture can pin that `'Unit'::cost` *resolves* into a
  sibling subtree; it cannot pin that the author *meant* the sibling. That residue honestly stays
  with the reader, and the guidance says so rather than implying the route checks intent.

---

## Integration Strategy

The exact route is the only route; nothing here adds a stage or an option. The F-3 repair makes an
existing refusal report like every other refusal. The migration moves the customer model onto the
form the codegen fixture has used since the cutover, so the two stop diverging on binding form — they
still diverge on `hif_driver_instance`, which is R-2's business and stays that way per D8. The
guidance rewrite replaces a section that contradicts the shipped route; `plant-idiom.md` already
carries the "reference fixtures live in sysml-codegen under `tests/fixtures/`" convention, so D3's
provenance links extend an existing habit — and D3's drift test is what turns that habit into a gate.

---

## Validation Approach

**Spine** — see The Spine above: the 11-formal enumeration plus two off-default mutations at two
occurrence depths, with the constraint consumer named.

**Necessary evidence, not sufficient:** generate, seal, snapshot on the migrated customer model with
zero readiness diagnostics; live and `--from-snapshot` packages byte-identical.

**Both paths refuse the self-named form:** codegen `SI_SELF_BINDING`, exit 1, empty output directory;
agentic-mbse `L2_SELF_NAMED_BINDING`, `success=False`; **and post-F-2** both accept D-6, which is what
makes "confirmed to refuse" an honest claim about *what* is refused.

**The teaching is falsifiable:** the self-named pattern returns zero unmarked hits across both trees;
the qualified-form audit is recorded site by site with its disposition; each promoted D-6 fixture's
conformance assertion passes by diagnostic name or entry-point value; the D3 drift test passes; the
full codegen suite green with the license loaded.

**The migration is bounded:** D5(a)–(d) all clear, and the strip check reports zero problems.

**Stellarator:** one run recorded — command, exit code, first refusal class and count, filed
follow-on. No fix, no reversal of the July hold.

---

## Next-Stage Handoff

**Fixed.** D-4 settled. D-5 as the recorded decision for the fusion-tea sites, with its reasoning.
One authoritative copy (D1). No push, no PR. R-2 pin stays (D8). ADR-010 filed decision-only (D9).
Stellarator triage-only (D10).

**Open, and named.** The usage-qualified measurement (D11 — the addendum is in flight). The `.claude/`
inventory and which tree is authoritative for agent instructions. The customer repo's actual site
list (D12). Whether F-2 needs `binding.py` changed.

**De-risk first, in this order.** (1) Re-verify B1 and re-run the corrected patterns over the whole
agentic-mbse tree — cheapest, license-free, and it sizes the rollout. (2) D12's customer-repo
discovery and D5's four preconditions — license-free, and the ones that can invalidate the mechanized
migration. (3) The D11 addendum — one fixture, one licensed run. (4) The F-3 repair, before the
renames run rather than after, so every later migration failure is legible.

**Surfaced, dependent conclusions parked.** The usage-qualified spelling behind all 13 published D-6
examples is unmeasured (D11). The `exploration/ife_e2e/models/` copy may carry self-bindings the
migration would leave behind (B8/D12). Neither is resolved here.

---

## Appendix A — The 15 customer binding sites and their D-5 targets

From `reverted/fusion-tea-model-migration.patch` against `tests/fixtures/fusion_tea/`. Verified
line-for-line by the review; the customer's line numbers match the fixture's.

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

Declaration side — 11 distinct names, **15 declaration lines**, 5 definitions, 3 library files (table
in Research Findings). `availability`, `gain` and `thermal_efficiency` each appear in two definitions.

## Appendix B — Measured behavior the guidance is written from

Condensed from `spike/findings.md`; that file, plus the pending D11 addendum, is the authority.

| shape | position | outcome |
|---|---|---|
| `in availability = availability` | anywhere | refused, `SI_SELF_BINDING` (both paths) |
| `in availability_in = availability` | inside the def | generates; entry point on the outer attribute; mutation moves it |
| `in driver_cost = driver.cost` | any | generates; entry point on that occurrence's feature |
| `in availability = 'Plant'::availability` (**definition**-qualified) | inside the def, 1 or 2 occurrences | generates; each occurrence reads its own value |
| `in unit_cost = 'Unit'::cost` | inside the def, 2 leaf occurrences below | refused, `SI_OCCURRENCE_AMBIGUOUS` |
| `in availability = 'Plant'::availability` | above the def, 1 occurrence | generates |
| `in availability = 'Plant'::availability` | above the def, 2 occurrences | refused, `SI_OCCURRENCE_AMBIGUOUS` |
| `in unit_cost = 'Unit'::cost` | no local occurrence, 1 in a sibling subtree | generates — resolves sideways (F-4) |
| `in length = geometry::input_length` (**usage**-qualified) | inside the usage | **UNMEASURED** — all 13 published examples, D11 |
| D-5 rename colliding with an `out` formal | — | traceback today; named diagnostic after D6 |
| D-5 rename colliding with a second `in` formal | — | `SI_OCCURRENCE_MISSING`, detail unreadable (filed) |

---

## Revision Record — rev 2

Six must-fix from `design-review.md`, plus the should-fixes and observations. Discovery was re-run
before any prose was amended, per the review's own instruction to gather evidence first.

| # | finding | resolution |
|---|---|---|
| **MF-1** | Inventory incomplete; grep under-inclusive | **Fixed at the root.** Pattern corrected to `\bin\s+[\w']+\s*=` and validated against `plant-idiom.md:79` before use; discovery re-run over `claude/`, `docs/patterns/` **and `project_templates/`**. Skill count 4→7; two template surfaces added. The one-authoritative-copy conclusion survived and was strengthened; D2 grew from one inline surface to three. |
| **MF-2** | "Bounded edit" concluded from one of three forms | **Fixed.** The qualified form is enumerated site by site: 13 positives across 5 files (table in Research Findings), plus 3 already-negative sites needing no change. Each gets a disposition under D11. The self-named audit was re-run with the corrected pattern and is unchanged at four. |
| **MF-3** | Every published D-6 example uses an unmeasured spelling | **Accepted; parameterised, not guessed.** All 13 are one uniform shape — qualification by the enclosing part usage. D11 pre-decides both branches; nothing publishes until the spike addendum lands. `MODELING_PROCESS.md.template:349` flagged as the highest-priority site because it teaches the unmeasured spelling as the fix for this very defect. |
| **MF-4** | Strip check cannot see `apply_aggregation_split` | **Fixed, and the limit written down.** Verified: zero rollup matches in the fixture, so latent not active; and `test_d5_variants.py:174-179` says a shape change cannot be proved by stripping a suffix. Closed by D5(d), a guard that refuses to run when a rollup matches. Required Invariant 4 restated to claim only what is enforced. |
| **MF-5** | Spine points at the wrong file; one consumer is not a module | **Fixed.** Confirmed `ife_plant.sysml` declares only a `part def` and mints nothing. New "The Spine" section names the site (`hif_plant.sysml:87`), the key (`hif_plant_pkg__hif_plant__gain`), and all three consumers individually — including `assert constraint viability` at `ife_plant.sysml:168` and its `formal_identity`. |
| **MF-6** | Site list is an assumed path list; a second synced copy exists | **Fixed.** D12 makes the list a discovery step over the whole customer repo including `exploration/ife_e2e/models/`; the six files become the expected result. Raised to a stated bet (B8) and treated as probably false. |
| **MF-7** | Spine proves 1 of 11 formals | **Accepted; fix changed.** Assertion 1 enumerates all 11 supplying attributes as entry points against the authored oracle, at no extra run. **Disagreement recorded:** the review's "mutate in a second design file" does not fit — `ife_plant.sysml` and `hif_driver.sysml` declare defs, not usages, so every design-attribute entry point roots at the one `hif_plant` usage. Widened by formal and occurrence depth instead (assertions 2 and 3). |
| SF-7 | Provenance has no drift check | Adopted — D3 now includes the conformance test over the packaged doc, with the broken-link failure and the partial-example exemption designed in. |
| SF-8 | Invariant 3 overclaims | Narrowed; the four unpinned shapes are named and labelled. |
| SF-9 | Invariant 2 constrains the counterexample's form | Stated explicitly, with the marker escape. |
| SF-10 | Duplicate pointer across two agent trees | `claude/` named authoritative on the symlink evidence; the residual hand-duplication named rather than hidden. |
| SF-11 | Non-Goal hardens a ratified agent-grade choice | Split: D-4 settled (owner); D-5-for-these-sites recorded as a decision with reasoning, challengeable. |
| SF-12 | Invariant 7 asserts an unenforceable agreement | Owner named (codegen owns, agentic-mbse mirrors), and "nothing catches drift" stated plainly. |
| SF-13 | Re-raise reclassifies internal failures | Sized in Implementation Notes with the keep-them-distinguishable rule; Invariant 6 extended. |
| SF-14 | Cycle naming is a traversal rewrite | Stated in D6 so the plan budgets for it; test on `s5_sibling_formal`. |
| SF-15 | Two unstated preconditions | Added as D5(c) and D5(d), and raised to bets B6/B7. |
| SF-16 | 11 names but 15 declaration lines | Table added; the plan counts lines, not names. |
| OB-17 | B1 point-in-time | B1 rewritten; re-verified this session; mitigation widened to the whole tree. |
| OB-18 | ADR title suffix; validation table | Both adopted in D9. |
| OB-19 | Fixture expectation-file obligation | Checked — none of the three declares a constraint; recorded in Component Overview. |
| OB-20 | Tool docstring inverted by D4 | Docstring update added to the rollout table. |
| OB-21 | Stale repo state | Updated to `7e95285`. |

**Endorsed by the review and carried unchanged:** the core concept and its three legs, D1, D2's
inline-plus-pointer split, the D-5 choice, D8's R-2 reasoning, D9, D10, both dispositioned repairs,
and Appendix A.

---

**Next Step:** the D11 addendum, then `/_my_plan`.
