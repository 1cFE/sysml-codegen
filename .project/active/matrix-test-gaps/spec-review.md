# Spec Review: Matrix Test-Gap Authoring (REQ-DM-08, REQ-RES-05, REQ-RES-08)

**Spec:** `.project/active/matrix-test-gaps/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/matrix-test-gaps/spec-review.md`
**Date:** 2026-07-07

---

## Reality Check

**Sound.** The spec is about the right work item, its code-facing claims check out against
HEAD, and the Route A ruling for DM-08 is honest. I verified the three rows independently:

- **DM-08** — wrappers are real `NewType`s (`identifier_types.py:24-43`); the model fields it
  originally pointed at are bare `str` (`resolution/models.py:54,111-120,155`); the doc admits
  DM-08 is open (`09-data-models.md:101-107`). Route A's premise is correct.
- **RES-05** — the outer `build_pipeline_context` pin exists and is a *different* function
  (`test_orchestrator.py:124`); `build_computation_graph`'s five internal milestones are real,
  distinct, source-ordered calls (`graph_builder.py:222/247/326/388/392`); the documented
  sequence is a genuine independent anchor (`03-resolution-overview.md:188-206`).
- **RES-08** — the three derivations are as described: backtracker `segments[1:-1]`
  (`dependency_backtracker.py:457-460`), aggregation `agg_parts[1:-1]` (`graph_builder.py:1383`),
  FORMULA owning-part scoping (`graph_builder.py:966,978-982`). The FORMULA divergence is
  **documented**, not hidden (`03-resolution-overview.md:70` Verified-by column).

The work item is sound. But there is one flagship defect — the DM-08 test's verification
mechanism is internally inconsistent with the surface it names — and one under-committed
reframe (RES-08's row text has the same INV-B tension DM-08 has). Both need a spec edit before
this becomes the plan's contract. Verdict: **Revise**.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The spec treats DM-08 as the *only* row whose text is forced to reframe
by INV-B, but RES-08's row text carries the same problem. The row reads "Consumer scope
derivation SHALL apply to ALL live resolution paths: backtracker (CalcUsage), attribute
resolution map (FORMULA), and `resolve_input()` (Aggregation) **via
`ResolutionContext.consumer_scope`**" (`03-resolution-overview.md:70`). FORMULA does **not** go
through `ResolutionContext.consumer_scope` — it scopes by owning-part QN (`graph_builder.py:966,
978-982`), and the row's own Verified-by column already says so ("FORMULA: scope via owning part
QN"). So the text and its verification column disagree, and a test that honestly asserts
FORMULA's owning-part mechanism will pin *less/other* than the "via consumer_scope" clause
claims. This is the DM-08 situation exactly. The spec only commits to reframing DM-08
(Non-Goals: "plus any RES-05/08 text the flip requires" — a maybe). Decide now whether RES-08's
row text needs the same reframe (drop or qualify the universal "via `ResolutionContext.consumer_scope`"
so it doesn't over-claim for the FORMULA arm), and whether "consumer scope derivation applies to
FORMULA" is itself honest given FORMULA derives no consumer scope — the [NEED] argues owner =
consumer for FORMULA, which is defensible but should be stated in the reframe, not left implicit.

**L1-2 · Direct claim (accuracy, holds):** The RES-08 mechanism-divergence framing is **honest**.
I checked for a papered-over inconsistency and found none: the doc row already documents the
three-mechanism split, so asserting three per-path mechanisms matches architectural intent rather
than hiding a bug. The [NEED] requirement (line 112-119) is accurate to the code.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim (the crux):** The DM-08 test as specified cannot be made mutation-provable
against the mutation the spec names, because the enforced surface it points at is not retained at
runtime. The spec pins "the `OutputRegistry` **registries** + `make_*` constructors carry them"
(lines 62-64, 73-75) and names the mutation "swap a **registry annotation** to bare `str`"
(line 99). The "registries carry them" surface is the dict annotations
`self._scoped: dict[ScopedKey, CanonicalChannel]` inside `OutputRegistry.__init__`
(`output_registry.py:48-55`). Those are **local annotated assignments on `self.x` targets** —
per PEP 526 they are not stored in any `__annotations__`, so `typing.get_type_hints` and every
runtime-introspection path cannot see them. A `get_type_hints`-style test therefore **passes
unchanged** when someone re-annotates `_scoped` to `dict[str, str]` — the exact named mutation
does not go red. The [HARD] "mutation-provable" requirement (line 98-101) is not satisfiable as
written.

There are two clean resolutions; the spec must pick one and make the named mutation match:
- **Source/AST scan** of `output_registry.py` (and `identifier_types.py`) — this *can* pin the
  dict annotations and *does* fail under the named mutation. The sibling test already uses this
  exact pattern (`test_orchestrator.py:97-117`, `inspect.getsource` + `ast`), so it is
  in-house-idiomatic.
- **Runtime introspection of the function signatures** — assert each wrapper is `NewType` over
  `str` (`SysMLQN.__supertype__ is str`), and assert the annotations on `make_scoped_key` /
  `make_canonical_channel` (return) and `register_scoped` / `register_sysml_qn` /
  `register_scoped_alias` (params) are the NewTypes. This is introspectable and mutation-provable,
  but then the named mutation must change to "re-annotate `register_scoped`'s key param to `str`,"
  not "re-annotate the registry dict."

Either is fine. Leaving it as-is ships an internal contradiction into the item whose entire point
is honest, mutation-provable pins.

**L2-2 · Note (surface hygiene, feeds L2-1):** "The enforced surface" is referred to five
different ways across the spec — "the wrappers ... and they are carried on the OutputRegistry
surface" (line 27), "registries + `make_*` constructors" (line 62), "`OutputRegistry` registries
+ constructors" (line 74), "registry dict annotations + register_*/make_* signatures" (review
prompt), "OutputRegistry keys/values and the make_* constructors" (the doc, `09-data-models.md:102`).
These are not the same set — dict keys/values vs. method params vs. constructor returns diverge
in exactly the way L2-1 turns on. Pin one canonical definition of the enforced surface and use it
everywhere, so the reframed row text, the test, and the mutation all name the identical thing.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** The DM-08 verification mechanism is missing from Open Questions. The
spec deliberately defers the RES-05 mechanism (source-order vs. spy) and the RES-08 test shape,
but says nothing about DM-08's — implying it is settled when L2-1 shows it is not. Since Item 3
skips the design stage (spec → plan → implement), the spec is the last checkpoint before an
implementer commits. Left unflagged, the plan is most likely to reach for `get_type_hints` (the
obvious "static test"), record some *other* passing mutation as the spot-check, and believe the
[HARD] requirement is met while the named mutation silently passes. Either resolve the mechanism
in the spec (L2-1) or add it to Open Questions with the same deferral discipline the other two
rows get.

**L3-2 · Rewrite request:** The Item-2 coupling re-check (lines 154-161) is not concrete enough
to execute mechanically. "Re-check Item 2's landed phases at implement time and extend the RES-08
enumeration if the climb has landed" gives a commit (`c7aecd6`, design) but no landed-signal an
implementer can test: no function/symbol to grep in `dependency_backtracker.py`, no plan-phase
checkbox to read. Make the re-check a concrete check — name the symbol the ancestor-climb
introduces (or the specific Item-2 plan phase), and state what the RES-08 backtracker arm would
assert *if* it landed (an ancestor-climb scope expectation, hand-authored) versus the HEAD case
(single `_consumer_scope_dotted`). As written, "extend the enumeration" is a decision punted to
an implementer who won't have the Item-2 context in front of them.

**L3-3 · Note:** RES-08's "ALL live resolution paths" invariant is, mechanically, an enumeration
of three named paths — its guarantee is exactly the completeness of that list, no more. A fourth
path (the Item-2 ancestor climb is the live candidate) is invisible to it until someone extends
the enumeration. That is inherent to enumeration tests and acceptable, but the row text should not
read as an exhaustiveness proof it cannot deliver. This is the same honesty concern as L1-1; fold
it in when deciding the RES-08 reframe.

**L3-4 · Note:** `register_alias` takes `ScopedKey | str` / `CanonicalChannel | str` for
backward compatibility (`output_registry.py:102-104`). If the DM-08 test asserts "every
registration method's key/value param is a NewType," it will fail on `register_alias`. Whichever
surface L2-1 lands on, the test must scope its target set to exclude (or special-case)
`register_alias` — worth a line in the plan so it isn't discovered mid-implement.

### Lens 4 — Hygiene

**L4-1 · Note:** The RES-05 documented sequence uses simplified names (`rebuild_groups`,
`topological_sort`, `validate_channel_references`, `03-resolution-overview.md:203-205`) that do
not match the code's call names (`derive_groups`, `_unified_topological_sort`,
`_validate_channel_references`). A source-order pin must map documented milestone → actual call
name; "rebuild groups" is `derive_groups()` + filtering, not a single call. Minor, but name the
mapping in the plan so the anchor set is unambiguous.

### Lens 5 — Reader Comprehension

No blocking finding. The R4 Finding / Ruling section (lines 43-69) is a clear, well-staged
account of why the naive flip fails and what Route A does. The one comprehension drag is the
inconsistent naming of the enforced surface, already captured as L2-2.

---

## Engagement Summary

**Overall take:** The work item is sound and the code claims hold — this is a well-grounded spec.
But the flagship DM-08 requirement has an internal contradiction: the surface it names (registry
dict annotations) is invisible at runtime, so the test it implies cannot go red under the mutation
it names. And RES-08's row text has the same INV-B over-claim DM-08 caught, which the spec only
half-commits to fixing. Both are spec-stage edits.

**Here's what I need you to weigh in on:**

1. **[L2-1, L3-1]** DM-08's enforced surface is not runtime-introspectable — pick the test
   mechanism (source/AST scan, which *can* pin the dict annotations and matches the sibling test;
   or runtime signature introspection, which forces the named mutation to change from "re-annotate
   the dict" to "re-annotate `register_scoped`'s param"). Make the named mutation match the choice.
   This is the one that breaks the item if left as-is.
2. **[L1-1, L3-3]** Decide whether RES-08's row text needs the DM-08 treatment. Its "via
   `ResolutionContext.consumer_scope`" clause over-claims for the FORMULA arm (which its own
   Verified-by column contradicts). Either reframe the row text or state explicitly why
   owning-part scoping counts as "consumer scope" for FORMULA.
3. **[L2-2]** Pin one canonical definition of "the enforced surface" and use it in the row text,
   the test, and the mutation — the five current phrasings name three genuinely different sets.
4. **[L3-2]** Make the Item-2 coupling re-check concrete: name the landed-signal (symbol or
   plan-phase) and what the ancestor-climb arm would assert, so the implementer can execute it
   without Item-2 context.

---

## Resolutions

*Filled in during Stage 5 as the human resolves findings.*

---

**Verdict:** Revise
**Next Steps:** Record resolutions above, then return to the spec-agent session (or re-run
`/_my_spec`) and point it at this review to incorporate. The reviewer does not edit the spec.
Once DM-08's mechanism (L2-1) and the RES-08 reframe question (L1-1) are settled, this is ready
for `/_my_plan` — the plan must carry the chosen DM-08 mechanism, the concrete Item-2 re-check,
and the three mutation spot-checks.
