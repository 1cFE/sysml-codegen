---
date: 2026-07-18T12:35:58-07:00
researcher: Codex
topic: "Final cross-repository gap and hygiene review for constraint expressions"
tags: [research, constraints, expression-ir, code-quality, pull-request, cross-repo]
status: complete
last_updated: 2026-07-18
---

# Research: Final Constraint-Expression Gap Review

**Date:** 2026-07-18 12:35 PDT

**Researcher:** Codex

**Research Type:** Codebase / Architecture / Cross-repository pull-request review

## Research Question

**[OWNER-VERBATIM]** “If you look at the git history and open PR, you will see major upgrades for
the constraint expressions (across agentic-mbse and sysml-codegen). we just made updates to close
gaps identified in a previous research report.

I want you to take one last run to spot any meaningful gaps, issues, or general code quality/hygiene
issues”

## Scope and Baseline

This pass reviewed the current remote PR tips, not the unrelated local commits one commit ahead:

- sysml-codegen PR #9 at `3f215ac30c0d92e0f0de82cc7bd2e26459eda0c9`;
- agentic-mbse PR #11 at `05cde35bd17377ddbd6bcc28823941ba43b4f69d`.

The review started from the two prior code-quality reports and checked their cures rather than
re-filing resolved findings:

- `.project/research/20260713-213722_constraint-exec-pr-code-quality.md`;
- `../agentic-mbse/.project/research/20260714-064234_constraint-exec-pr-code-quality-audit.md`.

It then focused on the v3 numerical-profile commits (`b251e95`, `05cde35`, `9c0291c`) and the
separable remediation commit (`da3b495`). Three independent passes reviewed profile semantics,
codegen/runtime behavior, and cross-repository hygiene. Every priority finding below was then
checked against the cited source and reproduced locally where a direct probe was practical.

## Summary

- The recent cures fixed the previous reports' central defects. Profile v3, equality exclusion,
  model construction validation, compiler shape checks, catalog exclusions, package verification,
  and focused live/snapshot behavior are materially stronger.
- The existing focused suites are green, but several meaningful correctness gaps remain. The two most
  serious are runtime arithmetic exceptions escaping the promised total evaluator and sanitized
  predicate-name collisions silently selecting the wrong predicate.
- The coordinated package contract is not installable from metadata. Both generations of
  agentic-mbse still identify as `0.1.0`, while codegen accepts any `agentic-mbse>=0.1.0`. Local
  editable installs hide this gap.
- New v3 paths have adversarial holes: mixed BLOCK/NON_NUMERICAL batches suppress warnings,
  anonymous excluded statements collide, malformed xor/implies arities warn, contradictory
  quantity facts can be admitted, and default-valued model fields bypass transactional assignment.
- The package-verification hardening still misses unrecorded directory symlinks. Several shipped
  docs teach v2 semantics, the execution lane is tied to one checkout path, both PRs have no
  reported CI checks, and branch-wide `git diff --check` is not green.
- I would not merge the wave unchanged. The fixes are localized; none requires the previously
  booked canonical-path/resolver architecture refactor.

## Priority Findings

| Priority | Finding | Classification |
|---|---|---|
| High | Admitted arithmetic can raise instead of returning evidence | Runtime correctness; inherited compiler gap exposed by v3 totality |
| High | Sanitized predicate function names can collide | Silent wrong-result defect; inherited generation gap |
| High | Package metadata cannot require the upgraded companion | Cross-repository release/installability defect |
| High | Mixed BLOCK + NON_NUMERICAL batches suppress warnings | New v3 behavior gap |
| High | Anonymous excluded assertions deterministically collide | New v3 exclusion-path defect |
| Medium | Failed assignment can leave a default-valued model invalid | New remediation defect |
| Medium | Malformed xor/implies arities warn instead of default-denying | New v3 profile defect |
| Medium | Contradictory quantity dimensions can bypass ratio validation | Malformed-wire totality defect |
| Medium | Verifier ignores unrecorded directory symlinks | New package-hardening gap |
| Medium | Durable docs still teach v2 or deny the lockstep dependency | User/release documentation defect |
| Low | Execution test lane and PR gates are not portable/automatic | Verification hygiene |
| Low | Export, docstring, complexity, and whitespace cleanup remains | API and review hygiene |

## Detailed Findings

### F1 — High: admitted arithmetic can raise instead of returning `ConstraintEvaluation`

The generated evaluator promises a verdict and says it never raises
(`src/sysml_codegen/templates/constraint_module.py.jinja2:1-5`). Profile v3 strengthens that into a
total contract: every admitted assertion compiles and executes
(`.project/active/numerical-constraint-profile/spec.md:35-39`).

The compiler emits raw division and exponentiation in the predicate body
(`src/sysml_codegen/generation/predicate_compiler.py:120-135`). It evaluates the arithmetic before
calling `_cmp` (`:170-181,260-270`). `_cmp` can turn already-produced `inf`/`nan` operands into an
indeterminate result, but it cannot catch exceptions raised while producing those operands
(`:59-71`).

Direct compiler probes reproduced both failures:

- `(a / b) > c` with `b=0.0` raises `ZeroDivisionError`;
- `(a ** b) > c` with `a=1e308, b=2.0` raises `OverflowError`.

Existing tests cover finite arithmetic and non-finite input leaves, not exceptional intermediate
arithmetic (`tests/unit/test_predicate_compiler.py:217-258`;
`tests/execution/test_constraint_execution.py:388-426`). This predates `9c0291c`, but v3's totality
claim makes it a current contract violation.

**[AGENT] Recommendation:** define exceptional numerical operations as indeterminate evidence and
guard generated arithmetic accordingly. Add division-by-zero, `0 ** negative`, exponent overflow,
and nested connective tests before merge.

### F2 — High: sanitized function-name collisions can execute the wrong predicate

The compile map is keyed by the raw predicate definition key, currently the usage qualified name
(`src/sysml_codegen/generation/constraint_catalog.py:43-54`). Function names are produced by
sanitizing and lowercasing that key (`src/sysml_codegen/generation/modules.py:117-131`). There is no
uniqueness check after this lossy conversion. All functions are emitted into one module
(`modules.py:135-153`; `templates/constraint_predicates.py.jinja2:1-11`).

A direct probe compiled two different predicates keyed by `Pkg::Foo-Bar` and `Pkg::Foo_Bar`. Both
became `constraint_pred_pkg__foo_bar`. Python keeps the later definition, so a wrapper importing the
first name executes the second predicate. Existing compile-once tests use one definition key and
cannot detect this (`tests/unit/test_constraint_emission.py:103-148`).

**[AGENT] Recommendation:** either reject post-sanitization/case-fold collisions with both raw keys
named, or append a stable hash derived from the raw key. Add a generated-module execution test with
opposite predicates and colliding names.

### F3 — High: dependency metadata cannot select the required companion implementation

Codegen imports agentic-mbse surfaces that do not exist on the base/released `0.1.0` tree
(`src/sysml_codegen/analysis/constraint_lowering.py:18-30`; `snapshot/loader.py:19-22`). The upgraded
agentic-mbse package still reports version `0.1.0` (`../agentic-mbse/pyproject.toml:5-8` and
`../agentic-mbse/src/agentic_mbse/__init__.py:7`). Codegen still declares only
`agentic-mbse>=0.1.0` (`pyproject.toml:23-25`). The editable sibling override masks this in every
local test (`pyproject.toml:64-65`).

The v3 design explicitly called for “an agentic-mbse version floor bump to the release carrying
v3” (`.project/active/numerical-constraint-profile/design.md:148-159`), but the audit certified SC 8
from the semantic string and recorded commit alone
(`.project/active/numerical-constraint-profile/audit.md:74-76`). A clean resolver may legally choose
the older `0.1.0`, then fail during import before the runtime semantic guard runs.

**[AGENT] Recommendation:** bump the companion package version and `__version__`, raise codegen's
minimum to that release, and add a wheel/install smoke test based on declared metadata. Keep the
documented #11-before-#9 merge order, but do not treat merge order as a package-version contract.

### F4 — High: a malformed sibling suppresses every non-numerical warning

`lower_constraints` computes BLOCK decisions and raises before entering the usage loop
(`src/sysml_codegen/analysis/constraint_lowering.py:752-769`). NON_NUMERICAL warnings are emitted
only later (`:775-786`). A direct batch probe containing one real-equality BLOCK and one Boolean-
equality NON_NUMERICAL statement produced `CodeGenerationError` and zero warnings.

This violates the design invariant that a NON_NUMERICAL statement yields exactly one warning in
each tool that runs (`.project/active/numerical-constraint-profile/design.md:238-242`). Current tests
cover BLOCK+ADMIT and NON_NUMERICAL alone, but not BLOCK+NON_NUMERICAL
(`tests/conformance/test_constraint_lowering.py:718-773`).

**[AGENT] Recommendation:** emit or aggregate NON_NUMERICAL warnings before the blocking raise.
Generation should still halt and should not emit a catalog, but valid out-of-scope statements in
the same model must not become silent.

### F5 — High: anonymous excluded statements collide and halt warn-and-continue

`_source_local_identity` correctly derives an anonymous identity from source location
(`constraint_lowering.py:456-469`). The non-ADMIT branch discards that component, normalizes every
missing qualified name to `"<anonymous>"`, and mints from only that placeholder, owner kind, and
source form (`:775-798`).

A direct probe with two anonymous Boolean-equality statements at lines 10 and 20 emitted both
warnings, then failed with the same `anonymous__anon__...` constraint ID. This contradicts the
warn-and-continue contract. The migration suite explicitly records that the corpus contains zero
anonymous constraints and cannot verify the join (`tests/conformance/test_constraint_migration_mapping.py:54-68`).

Eligible anonymous assertions have a broader inherited grouping limitation because their catalog
compile key is also `"<anonymous>"`. The new merge blocker is narrower: the v3 exclusion path
already has a location identity and throws it away.

**[AGENT] Recommendation:** include the location-derived `id_component` and owner identity when
minting excluded records. Add two-anonymous-statement tests for non-numerical, unassessed, and
eligible paths; book the eligible compile-key widening if it is not fixed in this PR.

### F6 — Medium: transactional assignment skips fields initialized from defaults

The remediation added `_TransactionalAssignmentModel` so a rejected assignment cannot leave an
invalid Pydantic object. Its prevalidation runs only if the field is already present in
`__pydantic_fields_set__` (`src/sysml_codegen/resolution/models.py:16-31`). Fields that took their
constructor defaults are absent from that set. `ConcreteConstraint.eligible=True` and
`exclusion=None` are both defaults (`:372-374`).

A direct probe built a valid eligible constraint while omitting both keyword arguments. Assigning
`eligible=False` raised `ValidationError` but left `eligible == False` with a predicate and channel.
Assigning an exclusion also raised but left the exclusion installed. The existing mutation test
constructs through a helper that explicitly passes the fields, so it misses this route
(`tests/unit/test_concrete_constraint_model.py:252-263`).

**[AGENT] Recommendation:** prevalidate every model field after initialization, using an
initialization-state guard rather than `fields_set` membership. Add default-omission mutation tests
and assert that the object remains unchanged and serializable after each rejected assignment.

### F7 — Medium: malformed xor/implies arities are treated as valid warnings

When v3 made `xor` and `implies` recurse for numerical-containment classification, it did not add
an arity gate (`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:604-620`). The adjacent
`and`/`or`/`not` branch checks its arity (`:623-640`). `OperatorNode` and its codec accept arbitrary
operand-list lengths (`../agentic-mbse/src/agentic_mbse/sysml/expression_ir.py:70-82,259-264`).

Direct probes produced `xor([]) -> NON_NUMERICAL` and one-operand `implies -> NON_NUMERICAL`. These
are malformed snapshot-valid shapes and should default-deny as BLOCK. Existing arity tests cover
only `and`/`or`/`not`; v3 tests use valid binary xor/implies
(`../agentic-mbse/tests/test_sysml/test_executable_profile_arithmetic.py:583-617`;
`test_executable_profile_v3.py:77-109`).

**[AGENT] Recommendation:** require exactly two operands for xor/implies and add 0/1/3-operand
codec-roundtrip tests.

### F8 — Medium: contradictory quantity facts can bypass the ratio unit gate

`_quantity_ratio_fact` admits equal exact-unit strings before comparing dimensions
(`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:293-309`). The general unit gate uses
the safer order: dimension mismatch before exact-unit mismatch (`:185-194`). `UnitFact` carries no
cross-field invariant and the codec reconstructs it verbatim
(`../agentic-mbse/src/agentic_mbse/sysml/expression_facts.py:37-48`;
`expression_ir.py:197-210`).

A direct probe divided `{unit=SI::metre, dimension=Length}` by
`{unit=SI::metre, dimension=Time}` and compared the result to `2`. The profile returned ADMIT with
no diagnostics. Live extraction should not create this shape, but malformed snapshot facts are an
explicit named-BLOCK responsibility.

**[AGENT] Recommendation:** validate dimension consistency before the equal-unit ratio admission
and add a serialized malformed-fact regression test.

### F9 — Medium: verifier ignores unrecorded directory symlinks

The extra-artifact walk calls `rglob("*")`, tests `is_file()`, and skips everything else
(`src/sysml_codegen/contracts/verify.py:263-298`). `Path.rglob` does not descend into a directory
symlink. A direct probe added `pkg/evilpkg -> ../outside`, where the outside directory contained
`evil.py`; `verify_package(...).ok` remained `True` with no diagnostics.

The hardening tests cover a recorded symlinked file escaping the package, not an unrecorded
directory symlink (`tests/unit/test_verify_package.py:193-209`). The missed directory can be an
importable Python package and is outside the recorded integrity surface.

**[AGENT] Recommendation:** treat any covered symlink as an artifact that must be explicitly
recorded and contained, or reject directory symlinks outright. Add internal and escaping directory-
symlink tests.

### F10 — Medium: shipped documentation is materially stale

The agentic modeling guide still teaches three outcomes, says BLOCK produces WARNING, admits
Boolean/string/integer/enum equality, and says xor/implies always block
(`../agentic-mbse/docs/patterns/constraints.md:25-41,252-295,321-342`). These docs are force-included
in the wheel (`../agentic-mbse/pyproject.toml:52-56`). Codegen's durable lowering doc likewise lists
only ADMIT/BLOCK/unassessed and omits `excluded_records`
(`docs/architecture/reference/28-constraint-lowering-and-catalog.md:8-15,51-73,83-87`).

The snapshot doc says agentic-mbse impact is “None” and that no lockstep surface exists
(`docs/architecture/reference/27-snapshot-generation.md:121-128`), while production has companion
schema pins and the v3 profile pin (`snapshot/loader.py:198-210`;
`constraint_lowering.py:747-751`). This is operationally dangerous beside F3.

**[AGENT] Recommendation:** update the three durable surfaces in the coordinated pair and add a
small doc-contract check for the four outcome names, v3 equality policy, and companion boundary.

## Code Quality and Hygiene Notes

- **Complexity increased at the semantic center.** `lower_constraints` rose from C901 12 to 18 and
  now also crosses the branch and statement thresholds (`constraint_lowering.py:720`). The profile
  already had complex arithmetic/value walkers; v3 raised `_walk_proposition` from C901 14 to 17
  and added `_walk_comparison` at C901 11. A mechanical file split would not help. Typed walk
  results and separate preflight/report/lower phases would.
- **The execution lane is machine-specific.** `tests/execution/conftest.py:6-9,22-27` hard-codes
  `/home/reid/1cfe/...`, inserts the path without checking it, and is excluded from default pytest
  (`pyproject.toml:44-50`). Another checkout receives an opaque `ModuleNotFoundError`. Discover the
  sibling relative to the repo, accept an explicit environment path, and validate it.
- **Neither PR reports CI checks.** `gh pr checks 9` and `gh pr checks 11` both returned “no checks
  reported.” The manual full-suite records are useful, but the merge wave has no automated signal
  that the required #11-first pairing and focused execution gates remain green.
- **Public API inventory is incomplete.** `ConstraintExclusion` and
  `ConstraintCatalogExcludedRecord` are nested field types but are absent from
  `resolution.models.__all__` (`src/sysml_codegen/resolution/models.py:538-557`). Export them or
  state that they are private.
- **Adjacent docstrings are stale.** `ConstraintCatalog` says its fingerprint covers only source
  and concrete entries, but code includes excluded records (`resolution/models.py:484-497`;
  `generation/constraint_catalog.py:132-142`). The snapshot loader comment points to an obsolete
  line number (`snapshot/loader.py:198-200`).
- **Diagnostic text does not fully match the v3 design.** Codegen warnings join only reason codes,
  not the actionable diagnostic messages promised by D5 (`constraint_lowering.py:779-786`;
  `.project/active/numerical-constraint-profile/design.md:169-176`). When numerical containment
  promotes a Boolean warning to BLOCK, the reason remains `warn_non_numerical_predicate` and its
  message still says the statement “is not executed,” rather than naming how to repair the mixed
  assertion (`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:730-740`;
  `tests/conformance/test_constraint_non_numerical.py:74-87`).
- **`git diff --check` is not green.** Codegen reports trailing whitespace in active remediation
  and numerical-profile artifacts plus older research/report EOF noise; agentic-mbse reports an
  extra EOF line in the archived executable-profile plan. Most is Markdown hard-break style, but
  it contradicts a literal branch-wide diff-check gate.

## Validation Performed

- sysml-codegen focused constraint suite: **119 passed, 13 skipped, 8 deselected**.
- agentic-mbse profile/validation suite: **140 passed**.
- optimized focused codegen suite: **118 passed, 5 skipped**. Note that Python `-O` also strips
  ordinary pytest assertions, so this is an import/control-flow check rather than full assertion
  evidence.
- Focused companion and codegen Ruff checks confirmed the documented complexity findings. The
  project-configured Ruff sets remain green as recorded by the prior closeout.
- Direct probes reproduced F1, F2, F4, F5, F6, F7, F8, and F9.
- GitHub inspection confirmed both PRs remain open at the recorded tips and report no checks.

The full licensed suites were not rerun in this research pass. Their latest recorded results remain
2450 passed / 26 skipped / 8 deselected for codegen and 1511 passed / 1 skipped for the companion.

## Architecture Insights

The remaining gaps do not invalidate the fact → ExpressionIR → profile → lowering architecture.
Most are boundary-totality failures:

```text
malformed or extreme input
        |
        +-- profile shape/unit checks ------> F7, F8
        +-- lowering identity/reporting ----> F4, F5
        +-- generated runtime/naming -------> F1, F2
        +-- model lifetime -----------------> F6
        +-- sealed-package boundary --------> F9
        +-- package/install boundary -------> F3
```

The previously booked parallel resolver ladders, triple instance walkers, live/offline orchestration
duplication, and exit-pin seam remain real architecture debt. They are already owned by
`[CONSTRAINT-ARCH-UNIFY]` and `[EXIT-PIN-SEAM]` in `.project/backlog/BACKLOG.md`, so this report does
not refile them.

## Feasibility Assessment

The blockers are localized and can be fixed without redesigning constraint resolution:

- F1 needs a runtime-safe arithmetic policy and generated helper;
- F2 needs collision-safe function naming;
- F3 needs coordinated package metadata;
- F4/F5 need lowering-order and identity corrections;
- F6-F9 each need one boundary guard plus adversarial tests.

The highest regression risk is F1 because it defines runtime semantics for exceptional arithmetic.
The others are mechanical once the intended contract is accepted. Documentation and hygiene can
land in the same closeout wave after behavior is settled.

## Recommendations

1. **[AGENT] Hold the merge wave for F1-F6.** They can crash, silently run the wrong predicate,
   break clean installs, suppress required output, reject valid anonymous statements, or leave
   invalid model objects.
2. **[AGENT] Fix F7-F9 before calling the boundary hardening complete.** They are small default-
   deny/integrity holes with direct reproductions.
3. **[AGENT] Refresh the durable docs and package metadata in both repositories together.** The
   implementation's semantic version is not a substitute for an installable dependency boundary.
4. **[AGENT] Add one adversarial cross-repo gate.** It should build/install the declared packages,
   compile colliding names, execute exceptional arithmetic, process mixed outcomes and anonymous
   statements, round-trip malformed IR facts, and verify directory symlink rejection.
5. **[AGENT] Keep the existing architecture follow-ons separate.** Fixing these gaps does not
   require reopening the canonical resolver/instance-index design before merge.

## Open Questions

1. Should division-by-zero and overflow produce indeterminate constraint evidence, or should they
   be explicit runtime evaluation failures? The current owner-level success criterion and template
   promise point to indeterminate, but that exact exceptional-arithmetic policy was not stated.
2. Are anonymous executable assertions a supported SysML authoring form for the first release? The
   identity helper says yes, while catalog compile grouping says no. The release contract should be
   explicit.
3. Is agentic-mbse meant to be installed as a package outside the sibling checkout? If yes, F3 is a
   release blocker. If no, the direct editable-source requirement must replace the misleading
   semver dependency.
4. Are directory symlinks allowed inside generated packages? The verifier needs an explicit policy
   either way; silently ignoring them is not an integrity policy.

## Key Code References

- `src/sysml_codegen/generation/predicate_compiler.py:59-71,120-181,240-270` — exceptional
  arithmetic escapes the Kleene runtime.
- `src/sysml_codegen/generation/modules.py:106-153` — lossy predicate function naming and shared
  module emission.
- `src/sysml_codegen/analysis/constraint_lowering.py:747-815` — v3 pin, blocking preflight,
  warnings, and excluded identity minting.
- `src/sysml_codegen/resolution/models.py:16-31,311-427` — transactional assignment and exclusion
  invariants.
- `src/sysml_codegen/contracts/verify.py:263-298` — extra-artifact traversal.
- `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:293-309,604-640` — ratio and
  connective shape gates.
- `pyproject.toml:23-25,64-65` and `../agentic-mbse/pyproject.toml:5-8` — dependency/version seam.
- `docs/architecture/reference/27-snapshot-generation.md:121-128` and
  `../agentic-mbse/docs/patterns/constraints.md:252-342` — stale durable guidance.
