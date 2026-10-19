# Semantics checks for the RG-1 candidates

Each candidate in `rg1-recommendations.md` gets a `kerml-expert` question and its answer here (plan PD10; P7 checks completeness). Citations are line numbers in the specification copies under agentic-mbse `docs/sysmlv2/`: `K:` is `SysML_KerMLSpec/full_document.md`, `S:` is `SysML_Spec_v2_Part1/full_document.md`, and library files are under `stdlib/`. The answers state what the specification says; SysIDE's own behavior was not checked for any of them.

## How the checks were run (Phase 4, 2026-10-18)

- Three invocations: G1 and G2 together, with both case models attached (PD10); the calc-usage bare result; and the stub causes, one question per cause in one invocation.
- Deviation: this worktree's `.claude/agents/kerml-expert.md` link is dangling (it points at `/home/reid/1cfe/...`). Each invocation ran as a general-purpose agent given agentic-mbse's `agents/kerml-expert.md` as its role, with the specification paths set to agentic-mbse's `docs/sysmlv2`. Read-only tools only.
- Deviation: the plan asks for one question per stub cause. They were asked as separate numbered questions in one invocation, not as separate invocations, because they share one base model.

## RG1-1 (G1): a redefinition that gives no multiplicity

**Asked.** In `part rack : Rack { part :>> servers; }`, where `Rack` declares `part servers : Server[2]` (and, in the second model, `[2] ordered`), what multiplicity and ordering does the redefining feature have? Models: `part-multiplicity__redefinition_drops_bounds__expanded_part_usage`, `g1__redefinition_drops_ordered_bounds`; control `part-multiplicity__exact_redefinition__expanded_part_usage`.

**Answer.** The redefining feature takes the redefined feature's `[2]` (S:3559-3567, S:4612; K:1637, K:1657, K:1673, K:8469, K:4652). For ordering, KerML says in prose that it "must also be ordered" (K:1643, K:1673) but gives no OCL rule for it, unlike uniqueness (`validateSubsettingUniquenessConformance`, K:5454); `isOrdered` is at K:5010-5012.

**Against today's generator.** One unindexed occurrence disagrees with the specification (two are required). Dropping the ordering disagrees with the prose. Whether the flag should read true, or whether omitting it is ill formed, the specification does not settle.

## RG1-2 (G2): a usage overriding a default that a bound reads

**Asked.** `part def Site { attribute n : Integer default 2; part racks : Rack[n]; }` with `part tuned : Site { attribute :>> n default 3; }` (case `g2__usage_override_of_referenced_bound`), and `part def BigSite :> Site { attribute :>> n default 3; }` with `part big : BigSite` (control `g2__definition_override_of_referenced_bound`). How many racks does each instance have?

**Answer.** A multiplicity bound is evaluated per instance of the owning type (K:8496, K:8502, example K:8505). A redefined value is the same on each instance (K:1657, K:1681). A default is not a binding (K:7004-7008, K:7024, K:7041; S:5330-5332), and the effective default is the owned one (K:8427-8431). Overriding is legal because `Site::n` is a default (K:7041). Not found: a rule for a bound whose referenced feature has only a default.

**Against today's generator.** `tuned` gets 2 racks and the specification gives 3; `big` gets 3 and agrees. Both overrides use the same mechanism in the language. Using a default as an occurrence count is the generator's own choice; the specification does not require a default to fix a multiplicity.

## RG1-3: a calc usage with its own bare result expression

**Asked.** In `calc m : Twice { in v = x; v * 3.0 }`, with `calc def Twice { in v : Real; return r : Real = 2.0 * v; }`, what does `v * 3.0` mean? Control: the same usage without the expression.

**Answer.** `v * 3.0` is the usage's result expression (S:11785-11801, S:7997-8001, S:8013, S:30505-30513; K:6205, K:6107-6112). A redefining usage keeps the definition's fixed binding (K:5370, K:2642-2646, K:8399-8410), so `r` must equal both `2.0 * v` and `3.0 * v`, which no value satisfies at `x = 1.0`. The specification advises that such a usage "should not include a result expression" (S:8016-8018; K:2228). `validateFeatureValueOverriding` (K:7041) covers feature values only. A type has at most one `ResultExpressionMembership` (K:6112, K:6166). A usage may narrow the definition but not contradict it; had the definition used `default` (K:2662), the usage's expression would be the result.

**Against today's generator.** It disagrees: it keeps the definition's expression and drops the usage's. The specification supports refusing a calc usage that carries its own result expression. Not checked: a SysIDE diagnostic, and the `Calculations::Calculation` library (S 9.2.12).

## RG1-4 to RG1-11: calc def output stub causes

**Asked.** For each construct in a calc def output, is it well formed and meaningful (so the stub is a generator capability gap), or ill formed (so refusing would follow the language)? One question per cause; base model `calc def C { in v : Real; return r : Real = …; }` used by `part def Gen`.

| Id | Construct | Answer |
|---|---|---|
| RG1-4 | `sum((v, 1.0))` | Well formed (K:2423; `NumericalFunctions.kerml:31, 34-36`; `RealFunctions.kerml:49-51`; K:8232). |
| RG1-5 | `v % 2.0` | Syntax valid (K:3373, K:3416, K:2339), but no Real remainder is defined: `NumericalFunctions::'%'` is abstract (`:21`), with concrete versions only for Integer (`IntegerFunctions.kerml:18`) and Natural (`NaturalFunctions.kerml:13`). Typing is a "should" (K:8385-8390). |
| RG1-6 | `return r : Boolean = true`; `return r : String = "liter"` | Both well formed (K:2547-2551, K:2552, K:2318, S:8016-8017, K:2186-2200). |
| RG1-7 | `v * pi` | Well formed; `TrigFunctions::pi` is fixed by an invariant (`TrigFunctions.kerml:9-10`, used at `:13`; K:13313). It is not a literal. |
| RG1-8 | members named `'if'` or `'1x'` | Valid unrestricted names (K:1015, K:1016, K:2923, K:2966-2968; `BooleanFunctions.kerml:10`, `DataFunctions.kerml:25`, K:8225). |
| RG1-9 | `v > 1.0`; `not b` | Both well formed, with Boolean results (K:3373, K:3404, K:8221-8225; `RealFunctions.kerml:30`, `BooleanFunctions.kerml:10`). |
| RG1-10 | `a = b + v; b = a + v; r = a` | Not ill formed: read as equations, it holds only when `v = 0` (K:2650, K:7004, K:7041, K:1992, K:5701). The circular-reference ban applies only to model-level evaluable expressions (K:6095, K:6408), which does not cover calc def members. |
| RG1-11 | `out attribute o : Real;` with no value | Well formed and unconstrained (S:6289-6291, S:7867-7868, S:7932-7934; K:2512). |

Not checked for any cause: what SysIDE reports.

## Completeness (Phase 7, 2026-10-19)

Every item design § F routes to a semantics check has a question and an answer above. Checked by hand against the stored answers and the record, not by a test (a test reading this file would break when the folder moves at close).

- **Candidate refusals:** 11 ids carry a `candidate_refusal` loss mark across 14 stored answers (`tests/expectations/subset_profile/cases/*.json`): RG1-1 (2 cases), RG1-2, RG1-3, RG1-4, RG1-5, RG1-6 (2), RG1-7, RG1-8, RG1-9 (2), RG1-10, RG1-11. Each id has an entry in `rg1-recommendations.md` and a question and answer here. No mark names an id outside RG1-1 to RG1-11.
- **G1 and G2:** RG1-1 and RG1-2 above, asked together with both case models (PD10).
- **`rg1_pending` disagreements:** none. `tests/expectations/subset_profile/disagreements.json` has 136 entries, 98 `reproduced_gap` and 38 `codegen_owned`.
- **O8 RG-1 candidates:** none. Phase 5 found no head site raising a plain exception, and Phase 6's one O8 conversion (`_typed_definition`, `ValueError` → `SI_TYPE_INVALID`) was refused before and after, so it was not a candidate.
