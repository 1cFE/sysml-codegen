# Design Review: Self-Binding Replacement — Establish, Document, Migrate

**Design:** `.project/active/self-binding-replacement/design.md`
**Spec:** `.project/active/self-binding-replacement/spec.md` (rev 3)
**Review File:** `.project/active/self-binding-replacement/design-review.md`
**Date:** 2026-08-15
**Reviewer state:** fresh session; codegen HEAD `9f5c40f` (the design's `Repo state` line says
`c334bdf`, two commits behind — harmless, but stale)
**Sandbox:** the same one the design had. `/home/reid/1cfe/agentic-mbse` and `/home/reid/1cfe/fusion-tea`
are unreadable from here. I verified every agentic-mbse claim through the same packaged tree
(`.venv/lib/python3.12/site-packages/agentic_mbse_data/`) and independently confirmed the hardlink
evidence (link count 2, identical mtime `1786807058`, on `plant-idiom.md`, the skill, and
`expose-pattern.md`). Customer-tree claims I could not check directly are marked as such.

---

## The Point

A modelled value bound as `in availability = availability` is legal SysML that does nothing. The
right-hand name resolves to the calculation's *own* input parameter, so the modelled attribute never
reaches the calculation and the calculation returns a confident wrong number on a default.

That is the direct negation of the product's promise. `P-001` says a designer varies parameters
freely and gets a viability answer they can trust; if a varied parameter never arrives, the answer
is wrong and nothing says so. The epic's Critical Success Factor (owner grade,
`.project/backlog/epic_elaborate_first_architecture.md:31-33`, verified) requires every consumed
modelled value to resolve to exactly one runtime source across all bound consumers, and an
unsupported authored form to fail loudly before generation. The `[OWNER]` mission invariant
(`:84-86`, verified) adds the observable: a public mutation reaches **every and only** the bound
consumers.

The owner restated the whole obligation on 2026-08-15 (`epic:71-78`, verified):

> "all I care about is: We know what the RIGHT pattern(s) are for the given situation / We document
> those right patterns / We fix the models to use the right patterns. `in R = R` is the wrong
> pattern. I would like to detect the use of it so we avoid it in the future. that's it, that's all
> I care about."

Four clauses, and the deliverable is all four. Generation and seal are necessary evidence, not the
goal. The rule must be **known** (measured on the shipped route), **documented** where humans and
agents actually read it, **applied** to the models, and the wrong form **confirmed refused** before
generation.

---

## Product-Lens Gate

**Gate: BLOCKED (design-F1, owner-graded).** Full block appended to
`.project/active/self-binding-replacement/product-lens.md`.

The lens ran independently and re-derived the point from the epic and the contract rather than from
the design's framing. It returned one BLOCK, five DISPOSE, and one DON'T (verified holdings). The
blocking finding is **design-F1**: the spine mutation check proves arrival for **1 of 11 renamed
formals and 1 of 3 migrated design files**. For the other ten formals the only evidence is
"generates, seals, snapshots with zero readiness diagnostics" — the absence-of-diagnostic gate the
epic's product-behavior rule forbids (`epic:84-86`, "never artifact-to-artifact fidelity"), and the
same gap this ledger's `spec-F4` already blocked once at spec scope. Its authority is the `[OWNER]`
mission invariant, so under `/_my_design_review` Stage 0 it controls the assessment below.

Two caveats on the lens run, surfaced rather than smoothed:

- It could not read `~/.claude/scripts/product-lens.md` (same sandbox denial the design hit) and
  reconstructed §3/§4 from the ~20 prior ledger blocks. Its reconstruction of the two design-level
  smells matches what `/_my_design_review` Stage 0 step 5 names independently, so the part carrying
  the gate is corroborated.
- Its epic line citations (`:59-66`, `:499-505`, `:78-80`) differ from the ranges I verified by
  reading (`:31-33`, `:71-78`, `:84-86`). Same statements, drifted ranges — a failure mode the
  Item-8 stocktake already named.

**Neither design-level smell fires.** *Consumer compensating for a producer guarantee* does not:
D7 moves the compensation the correct direction, fixing the name-based check in the producer rather
than making codegen tolerate a wrong flag. *Ownership of an invariant moving without saying so* does
not: the design meets the forward-flagged risk head-on in a named subsection, and the smell's hinge
is *without saying so*. I had initially read smell 7 as firing on Required Invariant 3's overclaim;
the lens's reading is better — the design says what it relies on, and the overclaim is a scope error
in the invariant's wording, not a silent ownership move. That is SF-8 below, not a fired smell.

**Smell 1 (two representations kept in sync by hand) fires twice** — design-F2 and design-F6 — both
disposed, neither blocking. Carried below as SF-10 and SF-12.

---

## Fundamental Assessment

**Fail — recommend Rework. The approach is right; the evidence base under three of the owner's four
clauses is not established, and the ledger gate is BLOCKED on the fourth.**

The design's core concept — *one rule, one authoritative copy, three legs of machine-owned
enforcement* — is the correct shape for this problem, and it is not over-engineered. It introduces
no new abstraction, no new pipeline stage, and no new detector. It reuses `make_d5_variant.py`,
extends an existing fixture-citation habit, and repairs two boundaries. A simpler design that met
the spec would have to drop something the owner asked for. I could not construct one.

The design also does several things well that a weaker design would have skipped. It surfaced its
own scope correction (D-5 renames the formal, so the brief's three-file list is undersized) instead
of quietly widening. It sized F-3 by locating the exact cause rather than asserting containment. It
took the smaller call on the R-2 pin and gave a checkable reason. Its Key Bets are mostly genuine
claims about reality with real "if false" consequences, not mechanism choices in bet costume.

What stops this from being Sound is not the approach. It is that **three conclusions the rollout
depends on rest on measurements that do not support them**, and I could falsify two of them from
inside the same sandbox the design worked in:

1. **The agent-instruction inventory is incomplete, and the grep that produced it is
   under-inclusive.** `project_templates/` — a tracked surface that seeds every new project's
   guidance — carries four calculation-binding examples, two of them owner-qualified, and appears
   nowhere in the design. The inventory grep also misses single-line bindings, including
   `plant-idiom.md:79`, one of the four examples this item exists to fix. (Must-fix 1.)
2. **"A bounded edit, not a sweep" was concluded from a grep for the wrong thing.** The design
   grepped for `in x = x` and found it confined to one file — correct, and I reproduced it with a
   stricter pattern. But the rule being published governs *three* forms. The owner-qualified (D-6)
   form is taught in **five** pattern docs with no statement of the position rule anywhere.
   (Must-fix 2.)
3. **Every published D-6 example uses a spelling the spike never measured.** The spike measured
   *definition*-qualified references (`'Plant'::availability`). Every D-6 example in the published
   docs is *usage*-qualified (`geometry_module::input_length`). The spec's own Change Record calls
   out that this distinction matters. The guidance rewrite would teach a position rule for a
   spelling with no measurement behind it. (Must-fix 3.)

On the forward-flagged smell 7, I initially read it as firing and have corrected that. The prior
lens block flagged: *if the design settles on "the guidance teaches it" for a behavior the route
cannot enforce, the loud-failure invariant has moved from the generator to the reader.* The design
answers this for F-4's sideways reach with a tracked fixture and a conformance assertion (D3,
`design.md:472-476`) and names the risk in a dedicated subsection. The smell's hinge is *without
saying so*, and this is said — so it does not fire. What remains is narrower and real: Required
Invariant 3 (`:353-355`) claims **every** taught shape is fixture-pinned, and at least four are not
— the inherited-attribute D-5 case (`plant-idiom.md:85`), the EXPOSE + D-5 case (`:200`), the
usage-qualified D-6 spelling, and the attribute-rename D-5 spelling (`:59-61`). That is an overclaim
in an invariant's wording (SF-8), not a silent ownership move. The lens makes the same distinction
about F-4 itself: a fixture can pin that `'Unit'::cost` *resolves* into the sibling subtree; it
cannot pin that the author *meant* the sibling, and that residue honestly stays with the reader.

Add the lens's blocking finding and the picture is that **the owner's four clauses each rest on
evidence that is not yet established**:

| owner clause | what it rests on | state |
|---|---|---|
| *know the right pattern for the situation* | the spike's measurements | established for definition-qualified D-6, **not** for the usage-qualified spelling every doc actually uses (MF-3) |
| *document those patterns* | the surface inventory and the "bounded edit" conclusion | **both wrong** — a missing surface, and an audit scoped to one of three forms (MF-1, MF-2) |
| *fix the models* | the six-file site list and the strip check | list is by assumption not discovery (MF-6); strip check forgives the tool's second edit (MF-4) |
| *confirm the wrong form refused* | `SI_SELF_BINDING` on both paths | **established** — this is the one clause that is solid |

And the verification leg — the spine that is supposed to prove the whole thing worked — covers 1 of
11 formals (MF-7, the lens's block).

**Why Rework rather than Revise.** I drafted this as Revise before the lens returned, on the
reasoning that each finding is individually bounded. That reasoning does not survive the tally. Every
one of these *is* individually cheap — extend a grep, run one more fixture, add one assertion — but
what they have in common is that the design reached conclusions from evidence that does not support
them, in four separate places, and the item exists precisely because published guidance drifted from
measured behavior. Amending the prose around unestablished claims would repeat the defect one level
up. The right move is to go get the evidence — all of it is license-free except the one spelling
measurement — and then let the design be rewritten against measurement. Under `/_my_design_review`
Stage 0 the owner-graded ledger BLOCK independently forces this answer; I am recording that it is
also the honest one.

**What survives Rework untouched.** This is not a redesign. D1's one-authoritative-copy call, D2's
inline-plus-pointer split, the choice of D-5 for the fusion-tea sites, D8's R-2 reasoning, D9's
decision-only ADR, D10's stellarator triage, and both dispositioned repairs (F-2, F-3) all hold — the
lens verified several of them independently and so did I. The rewrite is to the evidence base, the
rollout scope, and the verification design, not to the shape.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Fail

**The leading success criterion is not discharged.** The spec's spine — "an off-default mutation of
a migrated fusion-tea design attribute reaches every and only its bound consumers" — is a claim
about *the migration*, and the design's check covers one of the eleven formals the migration renames
and one of the three design files it edits (MF-7). For the other ten, the design offers zero
readiness diagnostics, which it correctly labels insufficient in its own words and then relies on
anyway. This is the same shape as `spec-F4`, which this ledger blocked once already at spec scope.
That, plus the three unestablished documentation claims below, is what makes this dimension Fail
rather than Concerns.

**Verified as met.** The spine mutation check exists and is correctly positioned as the criterion
that decides the item (`design.md:494-497`) — the defect is its coverage, not its presence or its
design. The measured-behavior criterion is served by treating `spike/findings.md` as authority
and by Appendix B. The "newly measured silent form is fixed or filed" criterion is served by D6/D7
plus the explicit filings in Non-Goals (`:420-421`). Stellarator triage-only (D10) matches the
`[NEED]` row exactly. `[HARD]` §7.17.2 is honoured (`:303-306`). The D-4 referent semantics survive
intact, and `Required Invariant 5` (`:356-358`) correctly protects the refusal fixtures, matching the
spec's Non-Goal.

**Concerns:**

- **The agent-surface criterion is not discharged by the design's inventory.** The spec requires
  that "every live surface that can instruct an agent about calculation bindings either carries the
  rule or reaches one authoritative copy" (`spec.md:83-86`). The design's inventory covers `claude/`
  and `docs/patterns/` only. `project_templates/` is missing. See Must-fix 1.
- **"No contradictory guidance left behind" is scoped to one of three forms.** See Must-fix 2.
- **The `[INFERRED]` parser-validation requirement is only partly discharged.** D3 substitutes
  fixture provenance for a snippet parser, and the reasoning for that substitution is sound — parsing
  proves the fragment is legal SysML, which is exactly what the four refused examples already are.
  But provenance-by-citation is a *pointer*, not a *comparison*. Nothing in the design fails when the
  doc text and the fixture text diverge, in either direction, and nothing checks them at publication
  time either. See SF-7 for a concrete closer.
- **Capture fidelity, minor.** The owner quote at `design.md:49-51` is truncated at both ends: it
  drops "all I care about is:" and "that's it, that's all I care about." Those bookends are the
  scope *limiter*, and this design then adds ten decisions and a codegen repair. The design inherited
  the truncation faithfully from `spec.md:100-103`, so this is a spec-level artifact, not a design
  defect — recorded so the next hop restores the full quote.
- **Provenance handling is otherwise clean.** The design correctly treats D-5…D-7 as ratified-`[AGENT]`
  and does not reopen them; it correctly treats the amended `SI_OCCURRENCE_AMBIGUOUS` row as measured
  fact; and it correctly surfaces the site-list correction as a scope correction rather than a premise
  conflict (`:128-132`) — that reading is right, and I confirmed it (`make_d5_variant.py:203-229`
  implements both halves, and the fixture proves the result).

### 2. Pattern Consistency
**Assessment:** Pass

- D3's provenance links extend an existing convention rather than inventing one; `plant-idiom.md`
  already carries "reference fixtures live in sysml-codegen under `tests/fixtures/`", and I confirmed
  the pattern docs already cite fixtures by name throughout (`plant-idiom.md:192-195`, `:208-209`).
- The F-3 repair uses the route's existing refusal vocabulary rather than adding one.
- Adding fixtures follows the existing shape (a `PROVENANCE.md` per fixture is the established
  convention — eight fixtures carry one today).
- **Verified, and worth stating because the design did not:** codegen's `.claude/agents/*.md` and
  `.claude/skills/sysml-conventions` are symlinks into `agentic-mbse/claude/` (the 37-file tree),
  not into `.claude/`. So D2's edit to `claude/skills/sysml-conventions/SKILL.md` reaches this repo's
  agents automatically. The `.claude/` divergence risk is agentic-mbse-local, which makes D1/D2 a
  better call than the design's own evidence showed.

### 3. Abstraction Quality
**Assessment:** Pass

No new abstraction is introduced. `--root` on `make_d5_variant.py` is a parameter, not a layer. The
three "legs" are a framing device in the prose, not three components. The one thing I probed for —
whether "one authoritative copy" is really a rule or really a new indirection layer — comes out as a
rule: the design deletes copies rather than adding a synchronizer, and explicitly rejects the
synchronize-copies alternative with the Item-7 A-1 evidence (`:214-217`). That is the right call.

### 4. Duplication Avoidance
**Assessment:** Pass

D1 is the whole answer here, and it is well argued. D2's "brief inline + pointer" is the correct
exception and its rejection notes are honest in both directions (`:218-222`). D9's refusal to put the
teaching text into the ADR (`:259`) is the same discipline applied consistently. I found one piece of
supporting evidence the design did not cite: `MODELING_GUIDE.md.template:145` and
`sysml-conventions/SKILL.md:210` carry the same binding example verbatim — the copy-drift D1 exists
to dissolve, already present.

### 5. Data Structure Clarity
**Assessment:** Pass

The design touches no data model. `ElaborationDiagnosticError` already takes a `Sequence[Diagnostic]`
and `GraphValidationError` already carries `.diagnostics` as a tuple of the same type
(`graph.py:82-88`, `elaborate.py:112-122`), so the D6 re-raise is a type-clean hand-off. The sketch
at `design.md:446-453` compiles against the real signatures.

### 6. Route Safety
**Assessment:** Concerns

The item adds no route, no option, and no fallback — good. Two safety concerns about the F-3 repair:

- **The re-raise reclassifies more than the cycle.** `elaborate.py:631` is the *only* unguarded
  `validate()` call on the live route — I checked all five call sites, and the other four
  (`instance_graph.py:1017`, `:1106`, `exact_pipeline_context.py:249`, `graph.py:896`) are already
  inside handlers. So the located cause is right. But `validate()` raises on the *whole* failure set,
  and most of that set is internal referential integrity (`graph.py:400-448`), not author error.
  After the change, a codegen invariant bug reads to the user as "Model failed exact-route
  validation" with exit 1 — a model refusal. See SF-13.
- **Naming the cycle participants is a traversal rewrite, not a payload edit.** See SF-14.

**Verified in the design's favour:** no existing test asserts `GraphValidationError` escaping through
`elaborate()`. The three tests that pin it (`test_elaboration_identity_collisions.py:92`,
`test_elaboration_projection_one_way.py:150`, `:160`, `test_projection_wiring_contract.py:120`) all
call `graph.validate()` or `project()` directly. The repair breaks nothing.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

**The stated bets are mostly genuine**, each with a real falsifier. B1, B2, B3 and B5 are claims about
reality, not mechanism choices. B4 is close to tautological ("the measured rule is the behavior of
the route") but it earns its place as a re-measurement trigger if the item lands on a later commit.

**B1 is weaker than stated.** It is written in the present tense ("is byte-identical"). What the
hardlink actually proves — and I reproduced it — is byte-identity *as of install time*, 08:17 today.
A `git checkout`, a stash pop, or most editors write a new inode and break the link silently. The
mitigation at `:459-462` re-greps `.claude/` only. It should re-verify the whole tree.

**B5 is true and I confirmed the mechanism**, but the design's use of it is wrong in a specific way.
See Must-fix 5.

**Three hidden bets, none stated:**

- **H1. That the tool's only edit is the rename.** It is not. `build_variant` also calls
  `apply_aggregation_split` (`make_d5_variant.py:224`), and `strip_check` undoes the aggregation
  rewrites *before* comparing bytes (`:262`). The repo's own test file says so in as many words:
  *"A shape change cannot be proved by stripping a suffix"* (`test_d5_variants.py:174-179`). See
  Must-fix 4.
- **H2. That renaming a left side is safe file-wide.** `_rename_binding_left_sides(text, name)`
  rewrites every `in <name> =` left side in a file, regardless of which def the usage is typed to.
  B3 covers sibling-formal collisions inside the declaring def; it does not cover a usage of a
  *different* calc def that happens to declare a formal of the same bare name. Eleven names across
  six files is enough surface for that to bite.
- **H3. That the customer model's binding sites live only under `models/`.** This repo's own record
  says fusion-tea keeps a synced second model copy at `exploration/ife_e2e/models/`
  (`.project/active/fusiontea-acceptance/plan.md:365-368`). See Must-fix 6.

**The decisions are well formed.** Every one of D1–D10 names its rejected alternative with a reason,
and the reasons are specific rather than ceremonial. D8's rejection note ("re-anchoring it here") and
D10's ("migrating its 15 copied-in files while we are in there") are exactly the temptations a
reviewer would probe, pre-answered. D4's two rejections are the right two.

### 8. Reader Comprehension
**Assessment:** Pass

A reader can skim this once and come away with the model. "One rule, one copy, three legs of
enforcement" (`:160`) is a real mental frame, stated before the mechanism, and the three legs are
each one sentence. The situational rule at `:163-169` is stated in plain words before any code. The
migration pipeline diagram at `:310-322` puts the proof visibly in the middle, which is the point of
it. Appendix A is the kind of table an implementer can work straight from — and it is correct, which
matters more.

One genuine comprehension defect, not a style nit: the sentence *"it resolves by your **position**"*
(`:167`) is doing a lot of work and the reader has to hold four clauses to unpack it. Given that this
is the rule the whole item exists to publish, and that the published version of it will be read by
agents, it is worth splitting into the two numbered steps the spike already wrote
(`findings.md:103-108`). That is a suggestion for the guidance text more than for the design.

---

## Issues by Severity

### Critical (must-fix — address before implementation)

**MF-1. The agent-instruction inventory is incomplete, and the grep that built it is
under-inclusive.** `design.md:76-92`, `:273`, `:368-376`, `:459-462`

`project_templates/` is a tracked instruction surface that seeds every new project's guidance, and it
carries calculation-binding examples the design never counted:

- `project_templates/MODELING_PROCESS.md.template:349-350` — `in volume = my_component::volume;`
  and `in surface_area = my_component::surface_area;` — the **owner-qualified form**, taught with no
  position rule.
- `project_templates/MODELING_PROCESS.md.template:365` — `in component_value = my_component.calculated_value;`
- `project_templates/MODELING_GUIDE.md.template:145` — `calc my_calc { in value = other_part.exposed_attr; }`

Separately, the inventory grep `^\s*in\s+\w+\s*=` is anchored to line start and a bare word. Over the
same skill file it returns 4 hits where a correct pattern (`\bin\s+[\w']+\s*=`) returns 7 — and the
three it misses include the single-line form. **The same blind spot would have missed
`plant-idiom.md:79`**, one of the four examples this item exists to fix. The plan is told to repeat
this grep over `.claude/`; repeating an under-inclusive grep produces an under-inclusive rollout.

*Action:* add `project_templates/` to the rollout table and Component Overview; state the inventory
pattern as `\bin\s+[\w']+\s*=` (or better, a fenced-block scan); re-run over the whole agentic-mbse
tree, not just `.claude/`.

**MF-2. "A bounded edit, not a sweep" is concluded from a grep for one of the three forms.**
`design.md:105-108`, `:350-351`

The design grepped for `in x = x`, found four hits confined to `plant-idiom.md`, and concluded the
edit is bounded. The self-binding half of that is right — I reproduced it with a stricter pattern
(`\bin\s+([\w']+)\s*=\s*\1\b`) across `docs/`, `claude/` and `project_templates/`, and the only hits
are `plant-idiom.md:40,42,46` (deliberate prose negatives) and `:79,84,85,200` (the four).

But the rule being published governs three forms, and the **owner-qualified form is taught in five
pattern docs with no position caveat anywhere**:

| file | lines | example |
|---|---|---|
| `expose-pattern.md` | 19-20, 66-67, 118-119 | `in length = geometry::input_length;` |
| `cross-file-binding.md` | 60-61 | `in length = geometry_module::input_length;` |
| `syntax-reference.md` | 93 | `in input_param = my_component::my_input;` |
| `adr002-calculations.md` | 106-107 | `in length = component::length;` |
| `project_templates/MODELING_PROCESS.md.template` | 349-350 | `in volume = my_component::volume;` |

Each of those is a shape whose safety is position-dependent by the measured rule, taught as if
unconditional. The spec's criterion is "no contradictory guidance left behind" — that audit has to
run over all three forms, not one.

*Action:* extend the "no contradictory guidance" check to the qualified and path forms; decide per
site whether it gets a caveat, a pointer, or a rewrite; record the enumeration.

**MF-3. Every published D-6 example uses a spelling the spike never measured.** `design.md:293-297`,
`:585-589`

The spike measured **definition**-qualified references throughout: `'Plant'::availability`,
`'Unit'::cost` (`findings.md` rows 4a–4e, 6). Every D-6 example in the published docs, and two of the
three shapes in the reverted customer patch (`hif_plant::thermal_power_gw`,
`hif_plant::availability`), are **usage**-qualified. The spec's own Change Record flags exactly this
distinction as a live correction: *"The SysML action example's qualifier points toward an enclosing
usage name, not the definition-qualified spelling used by ten sites in the reverted migration"*
(`spec.md:218-219`).

The design carries the measured rule into the guidance as if it covered both spellings. It may. It is
not measured, and this item exists because published guidance drifted from measured behavior.

*Action:* measure the usage-qualified spelling before the rewrite publishes a rule for it — one
fixture and one CLI run, which the spike's own `run_probe.sh` already does. If it is not measured,
the guidance must not state a rule for it. Park the dependent conclusion rather than smoothing it.

**MF-4. The migration tool does more than rename, and the strip check is built to forgive the
difference.** `design.md:229-233`, `:308-327`, `:351-352`, `:393-394`

`Required Invariant 4` says "The migration's only edit is the rename. Stripping `_in` reproduces the
originals byte for byte." The tool the design selects does not enforce that:

- `build_variant` calls `apply_aggregation_split(text)` unconditionally
  (`scripts/make_d5_variant.py:224`). That rewrite *introduces named intermediate attributes and
  restructures a rollup expression* (`:153-187`).
- `strip_check` computes `aggregation_rewrites(renamed)` from the source and undoes them from the
  variant *before* the byte comparison (`:261-262`). By construction, the strip check cannot see an
  aggregation split.
- The repo says so itself: *"A shape change cannot be proved by stripping a suffix, so these pin the
  summands, hand-derived numbers…"* (`tests/conformance/test_d5_variants.py:174-179`).

This is the exact question the review brief asked me to test — whether the bounded-diff check would
catch an arithmetic change hiding among renames. Against a hand edit, yes. Against the tool's own
second transformation, no.

**Measured mitigation:** I probed `tests/fixtures/fusion_tea` for the rollup shape
(`:>> <metric> =` followed by a newline) and found **zero** matches, so the split does not fire
there. If B2 holds, it likely does not fire on the customer tree either. The risk is latent, not
active — but the customer tree is unread and the invariant as written is not the one the tool
enforces.

*Action:* gate the run on `aggregation_rewrites(text) == []` for every customer file before writing
(one assertion, license-free), or add a flag that disables the split for the `--root` path. Then
restate Required Invariant 4 to match what is actually enforced.

**MF-5. The spine's mutation site is not where the design points, and one of the three consumers is
not a module.** `design.md:331-342`, `:494-497`

The design says *"`gain` is bound by three consumers in `ife_plant.sysml` (`:122`, `:146`, `:168`)"*
and then *"change the modelled `gain` off its default in the migrated customer model"*. Both halves
need correcting, and an implementer following this literally will not find the value to mutate:

- **`ife_plant.sysml` declares only `part def 'IFE Power Plant'` and no usage.** It mints no
  occurrence, no module, and no entry point. I confirmed this against the fixture's authored oracle:
  `FUSION_TEA_CLASSIFICATION` (`test_projection_wiring_contract.py:40-71`) contains 27 keys and not
  one of them is `ife_plant`-prefixed.
- **The mutation site is `designs/hif_ife/hif_plant.sysml:87`** — `:>> gain = 80.0`, under
  `part hif_plant : 'IFE Power Plant'` (`:8`). The key it mints is
  `hif_plant_pkg__hif_plant__gain`, `DESIGN_ATTRIBUTE` — which is the design's B5 confirmed, and it
  is the right key to read the "every and only" off.
- **The third consumer at `:168` is `assert constraint viability : 'Viability Threshold'`, not a
  calc.** `:122` is `lcoe_calc` and `:146` is `recirc_calc`. The *mechanism* holds — I checked, and
  so did the lens: `_regular_inputs` takes `CalcNode | ConstraintNode` on one path
  (`elaboration/project.py:503-539`) and `_build_constraint_modules` (`:845`) emits the constraint as
  a module, published as `hif_plant_pkg__hif_plant__viability__81ddf10fb1d1749b__evaluation`
  (`test_fusion_tea_real_teax.py:68`). So the check *is* achievable off `pipelines/pipeline.yaml`.
  The risk is enumeration: "all three consumer modules" written flat is easy to implement as "the
  three calc modules", silently dropping the one consumer class where "every and only" has
  historically been hardest — and the constraint consumer additionally carries `formal_identity`
  (`project.py:543`) that the calc consumers do not.

*Action:* name the mutation site with file and line, name the expected key, and name the constraint
consumer explicitly rather than saying "three modules". The spine is the criterion that decides the
item; it should be the most concrete paragraph in the document, and right now it is under-specified
at exactly the step that decides it.

**MF-6. The site list is enumerated by assumed path, and this repo records a second synced model
copy.** `design.md:128-132`, `:275`, `:399-404`, `:539-543`

The design's correction from three files to six is right as far as it goes — I verified the fixture
side line by line (below). But the enumeration method is a fixed path list, not discovery, and this
repo's own record says fusion-tea keeps a second model tree in sync:

> "Deleted `part hif_driver_instance` from BOTH `models/designs/hif_ife/hif_driver.sysml` and
> the `exploration/ife_e2e/models/` copy **(kept in sync)**" — `.project/active/fusiontea-acceptance/plan.md:365-368`

If that copy still exists and still carries self-bindings, the migration leaves it behind and the two
trees drift on binding form. I cannot check it from here — and neither could the design, which is
precisely why the enumeration should be a grep at plan time rather than a list at design time. Note
also that the reverted patch touched `models/` only, so it does not settle the question either.

*Action:* replace the fixed six-file list with a discovery step —
`grep -rnP "\bin\s+([\w']+)\s*=\s*\1\s*;"` plus a declaration-side grep for the 11 formals, over the
whole customer repo — and record what it returns. Keep the six files as the expected result, not as
the definition.

**MF-7. The spine proves arrival for 1 of 11 renamed formals and 1 of 3 design files.**
`design.md:331-342`, `:494-503` — *this is the product-lens BLOCK (design-F1), owner-graded.*

The mutation check covers `gain` in `ife_plant.sysml`. The migration renames 11 distinct formals
across 15 sites in three design files. For the other ten — everything in `hif_plant.sysml` and
`hif_driver.sysml` — the only evidence is "generates, seals, snapshots with zero readiness
diagnostics", which the design itself correctly labels necessary-but-not-sufficient. That is the
absence-of-diagnostic gate `epic:84-86` forbids, and it is the same gap `spec-F4` blocked once
already at spec scope; it has reappeared one level down.

The residual failure mode is real and silent: a renamed formal whose bare right-hand side resolves
to a same-named attribute in an *enclosing* scope produces no diagnostic and a wrong value. D5's
precheck inspects the **declaring def** for member collisions — it does not look at the usage-side
resolved referent, so it would not catch this.

*Action (cheap, and does not need a second full mutation):* after the one regeneration the design
already plans, assert that all 11 supplying attributes appear as entry points keyed on the supplying
attribute's display path — that is B5's rule applied as an enumeration rather than a spot check —
and add one off-default mutation in a second design file so `hif_plant.sysml` carries an arrival
check rather than a clean-generation check.

### Major (should-fix)

**SF-7. D3's fixture provenance has no drift check in either direction.** `design.md:223-228`,
`:353-355`

The reasoning for choosing provenance over a snippet parser is sound and I would keep it. But a
citation is a pointer, not a comparison. Nothing fails when someone edits the snippet in
`plant-idiom.md`, and nothing fails when the fixture changes underneath it. The spec's `[INFERRED]`
requirement is "parser-validated **before publication**"; provenance-by-citation discharges that only
through the author's care, which is what failed last time.

*Concrete closer:* a codegen conformance test that reads the packaged
`agentic_mbse_data/docs/patterns/plant-idiom.md`, extracts each fenced block carrying a provenance
marker, and asserts verbatim containment in the cited fixture file. Codegen already depends on
`agentic_mbse`, and the doc is readable from here — I read it for this review. Two caveats to design
around: `agentic_mbse_data` is a *copied/hardlinked* install (only `agentic_mbse` itself is editable),
so the test reads a snapshot and should fail loudly if the link is broken; and a doc example that is
deliberately partial will need an explicit exemption marker rather than a silent skip.

**SF-8. Required Invariant 3 overclaims — four taught shapes have no named pinning fixture.**
`design.md:353-355` vs `:368-376`, `:389-392`

The Component Overview names fixtures for plain D-5, D-7, and three D-6 positions. The taught set is
larger:

- the inherited-attribute D-5 case (`plant-idiom.md:85`, inside the retyping section);
- the EXPOSE + D-5 case (`plant-idiom.md:200`), which the spec names explicitly
  (`spec.md:80-82`);
- the usage-qualified D-6 spelling (MF-3);
- the attribute-rename D-5 spelling — `in length = plant_length`, "as `wi014_toy` does"
  (`plant-idiom.md:59-61`), a currently-published second form the design's situation 1 silently
  narrows away by teaching only the parameter rename.

*Action:* either name a pinning fixture for each, or narrow Required Invariant 3 to what is actually
pinned and say which shapes are taught on measurement-without-a-fixture. Do not leave the invariant
claiming more than CI holds — that is the failure mode this item exists to end.

**SF-9. Required Invariant 2 constrains how the kept counterexample may be written, and does not say
so.** `design.md:350-351` vs `:300-301` — *narrowed after the lens disagreed; recording both
readings.*

Invariant 2 demands zero hits from `grep -P "in (\w+)\s*=\s*\1\s*;"` across both trees, while
`design.md:300-301` keeps the negative "sharpened". I first read that as a contradiction. The lens
reads it as deliberate: the semicolon is what separates a *worked example* from a *warning*, so the
prose negatives at `plant-idiom.md:40,42,46` pass and a worked wrong example fails — which is the
intended acceptance.

That reading is better than mine, and I withdraw the contradiction claim. What remains is a real but
smaller constraint: the invariant silently forbids the counterexample from being written as a fenced
code block, which is the most natural way to sharpen it. Today's negatives pass by virtue of being
prose, and nothing records that this is load-bearing.

*Action:* state the constraint in the design — the counterexample stays prose or gets an explicit
marker (a `<!-- refused-by-design -->` comment or a `sysml-wrong` fence tag) with the invariant
reading "zero unmarked hits". One sentence; it stops a later author from sharpening the warning into
a code block and breaking the gate.

**SF-10. D1 removes the duplicate teaching but leaves a duplicate pointer, in the pair it cites as
drifting.** `design.md:214-217`, `:377-378` — *lens design-F2; smell 1, first instance.*

One authoritative copy removes the *teaching* from both `claude/` and `.claude/`. But D2's pointer
plus one-paragraph inline summary must now be planted in both, and Component Overview treats
`.claude/` as "the same treatment for whatever it finds". So the mechanism that produced Item 7's
A-1 residual survives at reduced size, and no decision says which of the two agent trees is
authoritative, or whether one is generated from the other. The design's own inventory could not
reach `.claude/`, so the duplication is unknown in size as well as unowned.

*Action:* after the `.claude/` inventory, state which tree is authoritative for agent instructions
and whether the pointer is duplicated deliberately or generated. Note my own finding that codegen's
`.claude/` symlinks resolve into `agentic-mbse/claude/` — that is evidence for `claude/` being the
authoritative tree, and it is checkable.

**SF-11. A Non-Goal hardens an agent-grade ratified choice into do-not-relitigate.**
`design.md:410-411` — *lens design-F4.*

"Reopening D-4 through D-7, or the choice of D-5 for the fusion-tea sites. D-6 turning out safer than
the spec assumed is not a reason to prefer it." D-4 is `[OWNER-VERBATIM]` and correctly settled.
D-5/D-6/D-7 and the D-5-for-fusion-tea recommendation are `[AGENT] (ratified by owner, 2026-08-05)`,
which capture-fidelity §1 makes challengeable by re-deriving against recorded reasoning — and the
recorded reasoning *did* change when the `[HARD]` row was re-measured on 2026-08-15.

The choice of D-5 still looks right on its merits (no qualifier, scales to repeated subsystems,
matches the shipped fixture), so this is about wording, not direction. As written it is the
"WE MUST NOT ⟨suggestion⟩" shape capture-fidelity §3 names — it anchors future agents on the
suggestion in a way the owner never expressed.

*Action:* split the Non-Goal. D-4 settled (owner). D-5-for-these-sites recorded as a decision with
its reasoning, challengeable on evidence.

**SF-12. Required Invariant 7 asserts a cross-repo agreement nothing can fail on.**
`design.md:361-362`, `:378-380` — *lens design-F6; smell 1, second instance.*

D7 fixes agentic-mbse's `level2_structure.py:350` by mirroring codegen's identity comparison, with
one test per direction — in agentic-mbse. Nothing in sysml-codegen fails if
`extraction/source_evidence.py:130-138` later drifts from that mirror. Two independent
implementations of one owner-verbatim rule (D-4), across two repos, agreement asserted as an
invariant, neither side deriving from the other.

Merging them is out of scope and should stay out.

*Action:* name the invariant's owner — which repo owns the rule, which mirrors it, and where drift
would be caught. If the answer is "nowhere", say that plainly rather than stating the agreement as
an invariant.

**SF-13. The re-raise reclassifies internal invariant failures as model refusals.** `design.md:384-387`,
`:446-453`

`validate()` raises on the whole failure set, and most of `graph.py:400-448` checks codegen's own
referential integrity, not authored model shape. After the D6 change, a codegen bug surfaces as
"Model failed exact-route validation" with exit 1 — indistinguishable from a user's bad model. F-3's
actual subject is one author-caused case: the producer cycle from a rename collision.

*Action:* say what stays distinguishable. Either keep the re-raise but make the cycle diagnostic
carry enough to tell the two apart, or narrow the catch. A one-line note in the design is enough;
this is a sizing decision, not a redesign.

**SF-14. Naming the cycle participants is a traversal rewrite, not a payload edit.** `design.md:240-243`,
`:387-388`

`_validate_producer_cycles` (`graph.py:862-892`) is a boolean DFS. `visit()` returns whether a cycle
was seen, keeps a `complete` memo that returns `False` for an already-visited node, and discards the
active stack on the way out. There is no path to recover. Producing the participant set means keeping
the stack at the moment of closure, or switching to SCC detection.

It is still one method and still contained — the disposition's "file it if it needs graph-layer
restructuring" bar is not met. But the design's framing ("carry the cycle participants into the
diagnostic") reads like a payload change and would mis-size the plan.

*Action:* say in the design that the traversal changes shape, so the plan budgets for it and covers
it with a test on the `s5_sibling_formal` shape.

**SF-15. Two unstated preconditions on the mechanized rename.** `design.md:234-238` (D5 precheck)

D5's precheck asks two questions per formal. Add two more, both cheap and license-free:

- **From H2:** for each of the 11 names, does any `in <name> =` left side in the six files belong to
  a usage typed to a def whose formal is *not* being renamed? `_rename_binding_left_sides`
  (`make_d5_variant.py:224`) rewrites file-wide and would silently break it.
- **From MF-4:** does `aggregation_rewrites()` return anything for any customer file?

**SF-16. The formal-declaration count is 11 names but 15 declaration sites.** `design.md:401-402`,
`:570-574`

Measured in the fixture: `ife_lcoe.sysml` ×7 (`:31,33,38,39,40,41,43`), `hif_economics.sysml` ×5
(`:25,27,57,100,101`), `fusion_cycle.sysml` ×3 (`:20,22`, plus the `constraint def` formal at `:47`).
Eleven *distinct names* across five defs, fifteen declaration lines, plus every in-body use. Note
`availability`, `gain` and `thermal_efficiency` each appear in two different defs. On an item whose
own headline finding is an undersized list, the plan's count should be the edit count.

### Minor (observations)

**OB-17. B1's evidence is point-in-time.** Verified (link count 2, mtime `1786807058` across
`plant-idiom.md`, the skill, and `expose-pattern.md`) — but a hardlink proves identity as of install,
and a `git checkout` in agentic-mbse breaks it silently. The mitigation at `:459-462` re-greps
`.claude/` only; extend it to the whole tree, and re-check the link counts as the first act.

**OB-18. ADR-010's title should carry the `(ADR-010)` suffix.** `design.md:255-259`. `CLAUDE.md`
prescribes `## N. Title (ADR-0NN)` and ADR-009 follows it
(`docs/architecture/modeling-assumptions.md:704`); sections 1–8 predate the convention. Also worth
deciding explicitly: the Validation Rules table at `:747-762` lists V1–V11 and does not mention
`SI_SELF_BINDING`. A reader asking "which rule refuses this?" reads that table. Say whether it gains
a row.

**OB-19. Adding fixtures carries one obligation, and it does not bite here.** Any new directory under
`tests/fixtures/` that declares a constraint needs an expectation file
(`test_constraint_population_oracle.py:81-110`). I checked all three promoted spike fixtures
(`s4b_qual_two_occ`, `s8_qual_outside_two`, `s6_qual_sibling_scope`) — none declares a constraint, so
no obligation attaches. Recorded so the plan does not rediscover it.

**OB-20. `make_d5_variant.py`'s docstring contract is inverted by D4, and the design says so.**
`:9-11` reads *"The originals are never touched. A variant is a new fixture beside the original."*
D4's in-place customer migration is the opposite, and `design.md:437-439` acknowledges it. Worth one
line updating the docstring when `--root` lands, so the next reader is not misled.

**OB-21. The design's `Repo state` line is stale.** `design.md:7` says `c334bdf`; HEAD is `9f5c40f`.
No consequence, but the F-3 line numbers are pinned to a moving file.

---

## What I checked and found sound

Recorded because the brief asked me to test these specifically, and a "no finding" answer is a
result:

- **F-3's containment claim holds (brief item 4).** `elaborate.py:631` is the only unguarded
  `validate()` call on the live route; the other four call sites are all inside handlers
  (`instance_graph.py:1017`, `:1106`, `exact_pipeline_context.py:249`, `graph.py:896`).
  `elaborate_model_paths` runs outside `_seal`'s try block
  (`exact_pipeline_context.py:272-280`), which is exactly why the traceback escapes. No existing test
  pins `GraphValidationError` escaping through `elaborate()`. The re-raise sketch type-checks against
  the real signatures. Contained — subject to SF-13 and SF-14.
- **The R-2 / `hif_driver_instance` reasoning holds (brief item 5).** The pin is
  `EXPECTED_CHANNELS` in `tests/execution/test_fusion_tea_real_teax.py:56-68`, and it runs against
  `FUSION_TEA = tests/fixtures/fusion_tea` (`tests/execution/real_teax.py:31`). That fixture still
  declares `part hif_driver_instance : 'HIF Driver'` at `designs/hif_ife/hif_driver.sysml:100` and is
  not a migration target — its 15 sites are already D-5. The migration edits the customer repo only,
  so the pin's subject is genuinely undisturbed. D8 is the smaller call and it is correct.
- **Appendix A is correct line for line.** All 15 fixture sites sit at exactly the line numbers the
  design lists (`ife_plant.sysml:114,116,121,122,123,124,126,146,148,168`;
  `hif_driver.sysml:73,75`; `hif_plant.sysml:186,215,216`).
- **The four refused examples are exactly where the design says**, and survive a stricter grep:
  `plant-idiom.md:79,84,85,200`, with the prose negatives at `:40,42,46`. No other packaged doc,
  skill, agent, command or template carries a self-binding.
- **The `claude/` tree inventory is accurate as far as it goes**: 5 agents, 15 commands, 10 skills
  (plus one hook), and `sysml-conventions/SKILL.md` is the only file in it that teaches calculation
  bindings. The four the design counted are correctly characterised as named-differently.
- **B5 confirmed:** `hif_plant_pkg__hif_plant__gain` is one `DESIGN_ATTRIBUTE` key in the fixture's
  authored oracle, and `is_self_binding` is genuinely identity-based
  (`extraction/source_evidence.py:130-138`), which makes D7's mirror target real.
- **D9's premise confirmed:** nine ADRs exist, next free id is 10, and no ADR or validation row covers
  binding resolution.

---

## Recommendations

1. **Fix the inventory before anything else** (MF-1, MF-2, OB-17). It is the cheapest step, it is
   license-free, and it is the one that sizes the rollout. Use `\bin\s+[\w']+\s*=` and run it over
   `claude/`, `.claude/`, `docs/`, and `project_templates/`.
2. **Measure the usage-qualified spelling** (MF-3) before the guidance states a rule for it. One
   fixture, one CLI run, through `spike/run_probe.sh`. If it goes unmeasured, do not teach it — park
   the conclusion and say so in the guidance.
3. **Close the tool's blind spot** (MF-4, SF-15) with a license-free assertion that
   `aggregation_rewrites()` is empty on every customer file, and restate Required Invariant 4 to
   match what is enforced.
4. **Make the site list a discovery step, not a path list** (MF-6, SF-16), and record what the greps
   return.
5. **Widen the spine to clear the ledger BLOCK** (MF-7). Enumerate all 11 renamed formals as entry
   points keyed on their supplying attribute after the one regeneration already planned, and add one
   off-default mutation in a second design file. This is the finding that gates the item.
6. **Specify the spine precisely** (MF-5): mutation site with file and line
   (`designs/hif_ife/hif_plant.sysml:87`), expected key (`hif_plant_pkg__hif_plant__gain`), and the
   constraint consumer named explicitly rather than "three modules".
7. **Reconcile the invariants with reality** (SF-8, SF-9, SF-12): narrow Invariant 3 to what CI
   actually holds; say that Invariant 2 constrains how the counterexample may be written; name who
   owns the cross-repo agreement Invariant 7 asserts.
8. **Add the drift check** (SF-7). A conformance test over the packaged `plant-idiom.md` turns D3's
   provenance from a convention into a gate, which is what the `[INFERRED]` requirement asks for.
9. **Settle the two-tree question and unharden the Non-Goal** (SF-10, SF-11): say which agent tree
   is authoritative once `.claude/` is inventoried, and split D-4 (settled, owner) from
   D-5-for-these-sites (a decision with reasoning, challengeable on evidence).
10. **Size the F-3 repair honestly in the design** (SF-13, SF-14) so the plan budgets for a traversal
    change and a classification decision, not a payload tweak.

---

## Resolutions

*(Stage 4 — filled in as the owner engages with this review. The design agent reads this section to
incorporate; the reviewer does not edit `design.md`.)*

---

**Overall:** **Rework** · **Product-lens gate: BLOCKED (design-F1, owner-graded)**

Not because the approach is wrong. The document is unusually honest about its own limits — it
surfaced its scope correction rather than quietly widening, sized F-3 by locating the exact cause,
and took the smaller call on R-2 with a reason I was able to verify independently. D1, D2, the D-5
choice, D8, D9, D10 and both repairs all survive.

It is Rework because the design reached conclusions from evidence that does not support them, in
four separate places, and the verification leg that would have caught that covers 1 of 11 formals.
Each fix is individually cheap. What they have in common is the failure mode this item exists to
end: a document stating something the measurements do not. Amending prose around unestablished
claims would reproduce that defect one level up.

**Next Steps:** Do not amend the design first — **gather the evidence first**, then rewrite against
it. MF-1, MF-2, MF-4 and MF-6 are all license-free greps and assertions. MF-3 needs one fixture and
one licensed CLI run through the spike's existing `run_probe.sh`. MF-7 needs one regeneration plus
one extra mutation. With those five in hand the design can be rewritten in a single pass and the
ledger BLOCK cleared by citation.

Record resolutions above, then re-run `/_my_design` (or return to the design-agent session) and
point it at this review. The reviewer does not edit `design.md`.
