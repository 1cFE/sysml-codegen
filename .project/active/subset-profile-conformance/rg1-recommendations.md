# RG-1 recommendations: losses and stubs that may need to block

Written in Item 2a Phase 4 (2026-10-18). Each entry is a construct the generator accepts today while losing part of the model, or replacing part of it with a manual stub. Under RG-1 (`briefs/align.md`) only the owner may change what the generator accepts or refuses, so nothing here changes behavior. Each entry pins today's behavior in a case, gives the semantics check, and recommends. The recommendations are `[AGENT]`; none is decided.

Each case named here carries a `loss` block with disposition `candidate_refusal` and this entry's id (`tests/expectations/subset_profile/cases/<case>.json`). `test_candidate_refusal_marks.py` holds that mark equal to the record's `candidate_refusal` qualification wherever a record cites the case. Only RG1-3 has a record mark. G1, G2 and the stub causes have no shared rule that isolates them, so only the case carries the mark (design D10). The semantics answers are in `evidence/semantics-checks.md`; SysIDE's own behavior was not checked for any of them.

How to read "recommend refuse": a refusal fails closed, so a modeller learns the construct is not supported. "Recommend keep the stub": the stub is the designed manual path, the run now announces it with a `ManualStubNotice` warning naming the cause, and the candidate mark can be withdrawn.

## Summary

| Id | Construct | Today | Recommendation |
|---|---|---|---|
| RG1-1 | G1: redefinition drops the redefined part's multiplicity | one unindexed occurrence, not two | refuse now; inherit bounds later |
| RG1-2 | G2: usage-level override of a default a multiplicity bound reads | override ignored, definition's count used | refuse the usage-level override |
| RG1-3 | calc usage with its own bare result expression | expression ignored, and the usage's input binding lost | refuse |
| RG1-4 | `sum(...)` in a calc def output | manual stub | keep the stub |
| RG1-5 | `%` on Reals in a calc def output | manual stub | keep the stub |
| RG1-6 | Boolean or String literal as a calc def result | manual stub | keep the stub; follows RG-2 for String |
| RG1-7 | library constant (`pi`) in a calc def output | manual stub | keep the stub; supporting constants is a capability item |
| RG1-8 | calc def member named a Python keyword (`'if'`) | manual stub, from a sanitizer mismatch | fix the mismatch (a defect, not a policy) |
| RG1-9 | comparison (`>`) or `not` in a calc def output | manual stub | keep the stub |
| RG1-10 | dependency cycle among calc def members | manual stub | refuse |
| RG1-11 | calc def `out` attribute with no expression | manual stub | keep the stub |

## RG1-1

**Question.** A part usage redefines a part whose definition gives it `[2] ordered`, and the redefinition gives no multiplicity (`part :>> servers;`). How many occurrences should the generator expand, and is the ordering kept?

**Cases.** `g1__redefinition_drops_ordered_bounds` (codegen home) and `part-multiplicity__redefinition_drops_bounds__expanded_part_usage` (agentic home). Control: `part-multiplicity__exact_redefinition__expanded_part_usage`, which restates `[2]` and gets occurrences `[0, 1]`.

**Today.** Generates. Seam `occurrences` on the redefined usage: count 1, index `null`, so one unindexed occurrence. The ordering is dropped too, so an `ordered` part that would be refused (`SI_MULTIPLICITY_UNSUPPORTED`) is accepted. The screen reports `part-multiplicity/ordered` admitted in context `unexpanded_part_usage`, because it sees the redefinition as a part usage the generator does not expand.

**Semantics.** The redefining feature inherits `[2]` (SysML S:3559-3567; KerML K:1657, K:8469), so one occurrence disagrees with the specification. KerML says in prose that a redefining feature of an ordered feature "must also be ordered" (K:1643), but has no OCL rule for it; whether the flag reads true is not settled.

**Recommendation.** Refuse a redefinition that omits the redefined part's multiplicity, with its own `SiteReason`, until the elaborator inherits bounds. Inheriting `[2]` is the correct long-term behavior. With today's rules it would then refuse the `ordered` case anyway and expand the unordered one to two occurrences. Refusing first is a one-site change that fails closed; inheritance is elaborator work for a later item. The record pair cannot carry the mark: `ordered`/`unexpanded_part_usage` also covers ordered usages that are correctly never expanded.

## RG1-2

**Question.** A definition's multiplicity bound reads an attribute whose value is a `default` (`attribute n : Integer default 2; part racks : Rack[n];`). A part usage overrides that default (`part tuned : Site { attribute :>> n default 3; }`). How many racks?

**Cases.** `g2__usage_override_of_referenced_bound` (codegen home). Control: `g2__definition_override_of_referenced_bound`, where a specializing definition overrides the default and the instance gets three racks.

**Today.** Generates two racks (seam `occurrences` count 2): the usage-level override is ignored and the definition's 2 is used. The Phase 1 probe (`evidence/g2-probe.md`) found the same.

**Semantics.** The bound is evaluated per instance (KerML K:8496, K:8502). The effective default is the usage's 3 (K:8427-8431), and overriding a default at a usage is legal (K:7041). So two racks disagrees with the specification and the definition-level control agrees. Treating a default as an occurrence count at all is the generator's own choice; the specification does not require a default to fix a multiplicity.

**Recommendation.** Refuse a usage-level redefinition of an attribute that a multiplicity bound reads, with its own `SiteReason`. The definition-level path already gives the right answer, so it stays. Evaluating the bound per occurrence is the long-term fix and belongs with the elaborator's occurrence work.

## RG1-3

**Question.** A calc usage ends its body with its own bare result expression (`calc m : Twice { in v = x; v * 3.0 }`), while the definition fixes `return r : Real = 2.0 * v`. Which result does the generator compute?

**Cases.** Packaged `calc-usage-result__bare_result__other_expression_site`. Control: `calc-usage-result__no_bare_result__other_expression_site`, the same usage without the expression. The four earlier `*__other_expression_site` cases also carry bare results and now show the same finding.

**Today.** Generates. Two losses, at three seams:

- The usage's expression is ignored. Seam `calc_compilability` on `fx::Site::m`: `fully_compilable`, output `r`, computed from the definition's `2.0 * v`. No output carries `v * 3.0`.
- The usage's input binding is lost too. Seam `contract_parameter` on `fx::Site::m`: `v` becomes a `library_default` entry point with a null default. Seam `entry_point` on `fx::Site::x`: none. In the control, `x` has entry point `fx__site__x` and `v` takes no parameter.

**Cause of the binding loss (a defect finding, not confirmed).** `_collect_bound_members` (`elaboration/elaborate.py`, near line 1894) iterates `getattr(usage, "owned_members") or ()`. On this usage that iteration yields the operator expression twice and never the `in v` member, while `.collect()` yields both. A likely cause is that the `or ()` truth test consumes SysIDE's lazy iterator; I did not confirm it. The control usage binds correctly, so this was only seen with a usage-level expression present. Fixing it changes generated output, not what is accepted, so it is outside RG-1; it needs a backlog item either way.

**Semantics.** `v * 3.0` is the usage's result expression (SysML :7997-8001, :30505-30513). A redefining calc usage keeps the definition's fixed binding (KerML :5370), so `r` must equal both `2.0 * v` and `3.0 * v`: unsatisfiable at `x = 1.0`. The specification supports refusing it. If the definition used `default` instead of `=`, the usage's expression would be the result.

**Recommendation.** Refuse a calc usage that carries its own result expression. The contract already reports it: rule `calc-usage-result`, shape `bare_result`, context `other_expression_site`, outcome `omitted`, qualification `candidate_refusal` (agentic-mbse `subset_profile_rules.toml`, matrix row CALC-USAGE-BARE-RESULT-DROP). If the owner accepts, the admission becomes `refused` with the new code, and the binding defect stops mattering for this shape but still needs its fix.

## RG1-4

**Question.** A calc def output calls `sum` (`return r : Real = sum((v, 1.0));`).

**Case.** `calc-def-output-stub__invocation`. Control for every stub entry: `calc-def-output-stub__compiled_control` (`return r : Real = 2.0 * v;`, `fully_compilable`, no stub). Twenty `binding-source__*` cases also stub this way (their `Total` calc sums `xs`).

**Today.** Generates with `r` as a manual stub (`MANUAL_REQUIRED`), cause `compile_invocation` (`extraction/calc_compat_renderer.py`, `_render`).

**Semantics.** Well formed (KerML K:2423; `NumericalFunctions::sum`).

**Recommendation.** Keep the stub and withdraw the candidate mark. `sum` is on the invocation allowlist the screen admits, the stub is the designed manual path, and the run now names the cause. Compiling `sum` in calc def outputs is a capability item.

## RG1-5

**Question.** A calc def output uses `%` on Reals (`v % 2.0`).

**Case.** `calc-def-output-stub__unsupported_operator_node`.

**Today.** Manual stub, cause `compile_ir_node_unsupported` (the expression IR has no node for `%`, so it is an unsupported node, not an unsupported operator).

**Semantics.** The syntax is valid, but the library defines `%` only for Integer and Natural, not Real.

**Recommendation.** Keep the stub. The model's meaning is unclear, and the stub hands the decision to the person writing the implementation, with the cause named.

## RG1-6

**Question.** A calc def result is a Boolean or String literal (`return r : Boolean = true;`, `return r : String = "liter";`).

**Cases.** `calc-def-output-stub__boolean_literal`, `calc-def-output-stub__string_literal`.

**Today.** Manual stub, cause `compile_literal_kind`: the renderer compiles only integer and rational literals.

**Semantics.** Both well formed.

**Recommendation.** Keep the stub. A Boolean or String result cannot feed the numeric pipeline as generated today, and a stub is the honest output. The String case should follow whatever RG-2 decides (`rg2-string-policy.md`).

## RG1-7

**Question.** A calc def output reads a library constant (`v * pi`).

**Case.** `calc-def-output-stub__library_constant`.

**Today.** Manual stub, cause `compile_reference_unresolved`: `pi` is neither an input nor a member of the calc def.

**Semantics.** Well formed; `TrigFunctions::pi` is fixed by an invariant.

**Recommendation.** Keep the stub. Rendering a known set of library constants is a small capability item.

## RG1-8

**Question.** A calc def member is named with a Python keyword (`attribute 'if' : Real = 2.0 * v; return r : Real = 'if' + 1.0;`).

**Case.** `calc-def-output-stub__python_keyword_member`.

**Today.** Manual stub, cause `compile_reference_unresolved`. The renderer's `_sanitize_name` and the extractor's sanitizer disagree: the member is registered as `if_` while the reference renders as `if`, so the lookup fails. A leading digit (`'1x'`) behaves the same.

**Semantics.** Both are valid unrestricted names.

**Recommendation.** Fix the sanitizer mismatch so the reference and the member agree. That is a defect fix that changes output, not acceptance. Until then the stub fails safe.

## RG1-9

**Question.** A calc def output is a comparison or a `not` (`v > 1.0`, `not b`).

**Cases.** `calc-def-output-stub__comparison_operator`, `calc-def-output-stub__not_operator`.

**Today.** Manual stub, cause `compile_operator_unsupported`: the renderer's operator map holds only `+ - * / ** ^`. Every one-operand operator other than `+` and `-` stops here too, so the unary-operator site is never reached (`mutations.json` unwitnessed).

**Semantics.** Both well formed, with Boolean results.

**Recommendation.** Keep the stub, for the same reason as RG1-6.

## RG1-10

**Question.** Two calc def members depend on each other (`attribute a : Real = b + v; attribute b : Real = a + v; return r : Real = a;`).

**Case.** `calc-def-output-stub__dependency_cycle`.

**Today.** Manual stub, cause `compile_dependency_cycle` (`extraction/expression_compiler.py`; no renderer site fires).

**Semantics.** Not ill formed as KerML states it: the ban on circular references covers only model-level evaluable expressions (K:6095). But read as equations it holds only when `v = 0`.

**Recommendation.** Refuse. There is no evaluation order, and a person writing the stub has nothing to implement that the model supports. A refusal tells the modeller the cycle is the problem.

## RG1-11

**Question.** A calc def has an `out` attribute with no expression (`out attribute o : Real;`).

**Case.** `calc-def-output-stub__output_without_expression`.

**Today.** `o` is a manual stub, cause `compile_no_expression`; `r` compiles.

**Semantics.** Well formed and unconstrained.

**Recommendation.** Keep the stub. This is the designed handwritten-implementation path: the modeller declared an output and left its computation to code.
