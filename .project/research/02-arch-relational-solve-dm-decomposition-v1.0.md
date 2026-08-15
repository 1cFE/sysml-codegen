# Relational Model Execution for SysML v2 Techno-Economic Analysis

**Dulmage–Mendelsohn decomposition as the compilation target for `teax`**

Version 1.0 · Research report · Status: proposal, not yet implemented

---

## 0. Executive summary

`teax` currently extracts SysML v2 `calc def` and `constraint def` elements, translates them
into Python assignment statements, wires them into a directed acyclic graph, and executes the
graph in topological order. This works and is in production use on fusion plant models.

It has three structural limits, all traceable to one decision: **solve direction is fixed at
authoring time.**

1. Algebraic loops cannot be expressed at all, in any direction.
2. Inverse questions ("what fusion power is implied by 500 MWe net?") require model rewrites.
3. Under-determination is an error, so design-space exploration has no native representation.

The proposed change is additive. Extraction stops emitting directed assignments and starts
emitting **undirected residual relations** carrying an admissibility annotation. A new compile
pass — bipartite matching, Dulmage–Mendelsohn partition, Tarjan SCC, topological sort —
determines solve direction, detects loops, and reports degrees of freedom. The existing DAG
executor survives as the fast path the compiler selects when every block is a singleton.

Nothing about the current SysML v2 authoring style has to change. `calc def` keeps its
directional semantics; that directionality becomes a restriction on the matcher rather than a
property burned into generated code.

**Effort estimate.** The graph algorithms are roughly 200 lines against SciPy and NetworkX, or
zero lines if Pyomo is adopted as the compilation target. The real work is (a) variable identity
and qualified naming, (b) a tier classifier for what math each relation contains, and (c) a
diagnostic layer that maps solver-level findings back to SysML element names. (c) is what
distinguishes this from a solver — and is where most of the product value sits.

---

## 1. Problem statement

### 1.1 Questions posed

This report responds to five questions raised while reviewing `teax` architecture:

| # | Question | Section |
|---|---|---|
| Q1 | What are the tradeoffs between expert-curated models with carefully chosen inputs/outputs, versus naive forward-only execution? | §2 |
| Q2 | Is there a general computational pattern for embedding solvers in a model-driven pipeline? | §4 |
| Q3 | What is the Dulmage–Mendelsohn step, and what form must each model component take to participate? | §4–§5 |
| Q4 | Why does extraction get *simpler* under a relational scheme? | §6 |
| Q5 | What classes of mathematics can a relation contain, how are they expressed in SysML v2, and how are they extracted into a Python primitive? | §7, Appendix A–B |

### 1.2 Current architecture

```
SysML v2 model
   ├── calc def        → directed: declared inputs, declared output, return expression
   └── constraint def  → boolean predicate, used for physical limit enforcement
        │
        ▼
   sysml-codegen
        │  · direct translation of math ops → Python
        │  · comment blocks → LLM-generated Python for complex math
        ▼
   DAG (edges by name matching; undriven inputs become model inputs)
        │
        ▼
   teax executor (topological order, single pass)
```

### 1.3 Where it breaks

**Cycles are rejected.** Recirculating power balance, sizing loops where structural mass depends
on the load it carries, counterflow heat exchange — these are genuinely simultaneous. They are
not a wiring mistake to be fixed; they are the physics. Current workarounds are hand-unrolling
the iteration or hiding the fixed point inside an opaque Python block, both of which move the
modeling decision out of the model.

**Direction is fixed.** The interesting fusion questions are inverse questions. "What would have
to be true for this concept to reach sub-1¢/kWh?" is not a forward evaluation. Answering it today
means authoring a second model.

**Under-determination is an error.** Every DAG leaf must be specified. There is no way to say
"leave three variables free and minimize LCOE over them subject to a divertor heat flux limit and
TBR ≥ 1.05." That is the shape of most real design work.

---

## 2. Directional vs relational

### 2.1 The distinction

The common framing is "custom expert model vs naive forward model." That framing is misleading —
it suggests a labor/quality tradeoff when the real difference is representational.

- **Directional (assignment).** `y := f(a, b)`. An instruction. Causality is asserted. The model
  *is* the procedure.
- **Relational (residual).** `r(y, a, b) = 0`. A statement of fact. No variable is privileged.
  Direction is a *view*, selected when the question is asked.

A relation carries strictly more information than the assignment derived from it. Going from
relation to assignment is a lossy projection. The architectural error in the current pipeline is
performing that projection during extraction rather than during compilation.

Note the corollary: a DAG is not an alternative to the relational scheme, it is a **special case**
of it — the case where every block in the decomposition is a singleton and the matching is the
one the author declared.

### 2.2 When directional is the right choice

Directional execution is not a naive fallback. It is correct and preferable when:

| Condition | Why directional wins |
|---|---|
| Causality is genuinely one-way | Cost rollups, mass rollups, aggregation hierarchies. Nothing to invert. |
| Every relation is an explicit function of upstream quantities | No loops, no ambiguity. |
| The audience is auditors or reviewers | A single-pass evaluation is trivially traceable. Every regulator-facing TEA in existence is a spreadsheet for this reason. |
| Speed matters and the model is called in a tight loop | No matching, no Newton, no Jacobian. Substitution only. |
| The model is small enough to reason about unaided | The compilation machinery is overhead. |

**This describes the large majority of TEA models.** The relational scheme must not make this case
slower or harder to read, which is why the DAG executor is retained rather than replaced.

### 2.3 What forward-only cannot do

| Failure | Example from fusion TEA |
|---|---|
| **Algebraic loop** — variable appears on both sides through a cycle | `P_recirc = f · P_gross`, `P_gross = P_thermal · η`, `P_net = P_gross − P_recirc` with `f` itself a function of `P_net`. No topological order exists. |
| **Implicit single relation** — variable appears twice in one equation | Colebrook friction factor: `1/√f = −2·log₁₀(ε/3.7D + 2.51/(Re·√f))`. No closed form. |
| **Inverse / requirement-driven solve** | "Given 500 MWe net and a divertor at its 10 MW/m² limit, what `P_fusion` and `A_div` does that imply?" |
| **Degree-of-freedom analysis** | "This model has 4 DOF; which variables are eligible to be free?" |
| **Over-specification diagnosis** | "You have specified 12 quantities but the model admits 10; the conflict localizes to `{P_fusion, A_div}`." |
| **Constraint-as-target inversion** | Treating a physical limit as an equality that *defines* a design point rather than a check applied afterward. |

The last row deserves emphasis given the current use of `constraint def` for limits. A limit used
as a post-hoc check answers "is this design viable?" The same limit used as an active equality
answers "what design sits exactly at the limit?" — which is where optimal designs live. Under the
relational scheme this is a change of analysis case, not a change of model.

### 2.4 Capabilities unlocked, ranked by value

**1. Degrees of freedom become first-class.** The Dulmage–Mendelsohn partition does not merely
count DOF — it identifies *which* variables are structurally eligible to be free. DOF count is a
property of the model; which variables fill it is a design choice. This turns the model from an
evaluator into a description of a design space, and is the prerequisite for coupling to an
optimizer.

**2. One model, many questions.** Forward evaluation, inverse solve, sensitivity, and optimization
all compile from the same source. Only the known/unknown partition changes. This is the argument
that a formal model is worth authoring at all: the alternative is N spreadsheets that drift.

**3. Algebraic loops become expressible.** Fixed points move out of opaque code and into the model,
where they are visible, checkable, and differentiable.

**4. Structural diagnostics.** Over- and under-determination localize to specific relations and
variables. This is a class of error the current pipeline cannot detect and cannot report.

**5. Constraints gain dual roles.** The same `constraint def` is a viability check when the system
is square and a feasible-set boundary when DOF exist. Determined by the compiler per analysis case.

**6. Exact derivatives.** Symbolic residuals give analytic Jacobians via AD, which serves both
Newton and gradient-based optimization, and provides sensitivities for free.

### 2.5 The honest middle ground

A forward model plus automatic differentiation recovers a large fraction of expert intuition —
gradients, sensitivities, local inversion via Newton on the composed function — at far lower
complexity than a full relational compiler. It is the correct answer when the question is "what
matters most here?"

The relational form earns its complexity specifically when:

- the system is genuinely simultaneous (AD does not create a solution where none exists in order), **or**
- the DOF structure is the object of interest, **or**
- one model must serve many differently-directed questions over time.

Fusion TEA hits all three. Not every domain will.

---

## 3. Prior art

This is a solved problem in process systems engineering. The pipeline below is standard in:

| System | Domain | Notes |
|---|---|---|
| **Modelica** (Dymola, OpenModelica) | Multi-domain physical modeling | Reference implementation. Flattening → BLT → tearing → index reduction. Handles DAEs, which is out of scope here. |
| **gPROMS** | Process engineering | Equation-oriented, explicit DOF management. |
| **Aspen Custom Modeler** | Chemical process | Equation-oriented alongside Aspen Plus's sequential-modular mode — the same directional/relational split described in §2. |
| **Pyomo** (`contrib.incidence_analysis`) | Optimization, open source | Provides DM partition and block triangularization directly. <cite index="5-1">`IncidenceGraphInterface.dulmage_mendelsohn()` partitions variables and constraints into square, underconstrained, overconstrained, and unmatched sets.</cite> |
| **JuMP / Julia** | Optimization | Similar tooling in `ModelingToolkit.jl`, including structural simplification. |
| **EMSO, Ascend IV** | Academic EO modelers | Ascend is the closest philosophical ancestor: declarative models plus explicit DOF management. |

Key literature:

- Dulmage, A.L. & Mendelsohn, N.S. (1958). "Coverings of bipartite graphs." *Canadian Journal of Mathematics* 10, 517–534. Original decomposition.
- Pothen, A. & Fan, C.-J. (1990). "Computing the block triangular form of a sparse matrix." *ACM TOMS* 16(4), 303–324. The practical algorithm.
- Duff, I.S., Erisman, A.M. & Reid, J.K. *Direct Methods for Sparse Matrices*, 2nd ed. Oxford, 2017. Ch. 6 on matching and BLT.
- Elmqvist, H. (1978). *A Structured Model Language for Large Continuous Systems*. PhD thesis, Lund. Origin of the Modelica compilation approach.
- Cellier, F.E. & Kofman, E. (2006). *Continuous System Simulation*. Springer. Ch. 7 on tearing and structural analysis.
- Pantelides, C.C. (1988). "The consistent initialization of differential-algebraic systems." *SIAM J. Sci. Stat. Comput.* 9(2). Index reduction — relevant only if DAEs are later admitted.

**Implication for M-Scout positioning.** The solver layer is not a differentiator. The
differentiators are the SysML v2 source of truth, LLM-assisted population of the model and catalog,
and diagnostics expressed in domain terms. A defensible architectural statement is: *SysML v2 is
the source of truth, the solver layer is a compilation target, and we are deliberately not writing
another Newton solver.*

---

## 4. How relational models are built

### 4.1 The canonical form

Every relation, regardless of whether it originated as a `calc def`, a `constraint def`, a catalog
lookup, or an external code wrapper, normalizes to the same record:

```
Relation
  id            : stable identifier
  source        : SysML qualified name          # for diagnostics — load-bearing
  kind          : "eq" | "ineq"
  tier          : 0..4                          # what math it contains (§7)
  vars          : {VarRef}                      # EXACT and COMPLETE incidence set
  solvable_for  : {VarRef} ⊆ vars               # which variables may be matched to it
  direct_for    : {VarRef} ⊆ solvable_for       # which can be isolated in closed form
  residual      : r(x) = 0                      # symbolic, or None for tier 4
  evaluate      : callable                      # fallback for opaque relations
  jacobian      : sparsity pattern + AD handle
  cost          : "free" | "seconds" | "minutes"
  validity      : domain bounds, provenance
```

Variables carry `{id, dimension, unit, domain, bounds, scale, initial_guess}`.

**`known` is not a property of the variable.** It belongs to the analysis case. That partition is
the thing you swap to change the question — and it is the single most important design decision
in this scheme.

Normalization examples:

| Origin | Residual | `solvable_for` |
|---|---|---|
| `calc def` returning `y = a·b` | `y − a·b` | `{y, a, b}` — all isolable |
| `calc def` with `invertible = false` | `y − f(a,b)` | `{y}` only |
| `constraint def` with `==` | `lhs − rhs` | whatever is isolable |
| `constraint def` with `<=` | `lhs − rhs` (slack form `g(x) ≤ 0`) | `{}` — excluded from matching |
| External code (neutronics, CFD) | none — opaque callable | `{output}` only |
| Catalog table, monotone PCHIP | `k − interp(T)` | `{k, T}` |

Note that `calc def`'s declared output does **not** force `solvable_for = {output}`. It forces
inclusion of the output; the compiler may still discover that other variables are isolable. This is
the mechanism by which existing models gain inverse capability without being rewritten.

### 4.2 The compilation pipeline

```
1. FLATTEN        resolve hierarchy, inheritance, instantiate usages
2. NORMALIZE      each element → Relation record  (element-local, stateless)
3. RESOLVE        variable identity: qualified names, bind-through, union-find
4. CHECK UNITS    dimensional consistency pre-pass
5. PARTITION      apply analysis case: known vs unknown
6. MATCH          maximum bipartite matching over admissible edges
7. DECOMPOSE      Dulmage–Mendelsohn coarse → under / square / over
8. TRIANGULARIZE  Tarjan SCC within square part → block lower triangular
9. SEQUENCE       topological sort of blocks
10. DISPATCH      per-block: substitution | linear | Newton | homotopy
11. EMIT          residual fn + sparse Jacobian, or objective + constraints for outer loop
```

Steps 1–4 run once per model. Steps 5–11 run per analysis case. This split matters: it means the
expensive extraction work is amortized across every question asked of the model.

### 4.3 Matching and decomposition, in detail

**Bipartite graph.** Rows = relations, columns = variables. Edge (i, j) exists if variable *j* is
in relation *i*'s incidence set. The edge is **admissible** only if *j* ∈ `solvable_for(i)`. Before
matching: drop columns for known variables, drop inequality rows entirely.

**Maximum matching.** Hopcroft–Karp, O(E√V). Assigns each relation the one variable it is
responsible for computing.

**Dulmage–Mendelsohn coarse partition.** Splits the graph into three parts. Critically, this
partition is **canonical** — independent of which maximum matching was found.

| Part | Meaning | Action |
|---|---|---|
| **Under-determined** (horizontal) | More variables than relations | These are the degrees of freedom. The variables in this block are exactly the promotion candidates for "what can I leave free?" Either specify more, or hand to an optimizer. |
| **Well-determined** (square) | Perfect matching exists | Solve it. Proceed to fine decomposition. |
| **Over-determined** (vertical) | More relations than variables | Either inconsistent, or over-specified. The variables here are exactly the candidates to release. |

The over-determined block is the diagnostic that the current DAG cannot produce. It converts
"solver did not converge" into "`PowerBalance::netPowerConstraint` and
`DivertorLimit::heatFluxConstraint` are both binding over `{P_fusion, A_div}`; release one."

**Fine decomposition.** Within the square part, orient the graph using the matching: contract each
matched (relation, variable) pair into a single node; add edge u → v if u's relation contains v's
matched variable. Run Tarjan SCC. Topologically sort the condensation. Result is block lower
triangular form.

- **Singleton blocks** → direct substitution (the current DAG behavior).
- **Larger blocks** → irreducible simultaneous systems requiring Newton.

**Tearing** within large blocks — choosing a small set of iteration variables so the rest solves by
substitution — is optional and NP-hard to optimize. Heuristics only. Not required for a first
implementation; a dense Newton on a 5×5 block is fine.

### 4.4 Worked example

Six relations, a fusion power balance with a divertor heat flux calculation:

```
eq1: P_thermal  = P_fusion · (1 + M_blanket)
eq2: P_gross    = P_thermal · eta_th
eq3: P_recirc   = f_recirc · P_gross
eq4: P_net      = P_gross − P_recirc
eq5: P_div      = P_fusion · f_div
eq6: q_div      = P_div / A_div
```

**Case A — forward.** Known: `P_fusion, A_div, M_blanket, eta_th, f_recirc, f_div`.
Matching: eq1→P_thermal, eq2→P_gross, eq3→P_recirc, eq4→P_net, eq5→P_div, eq6→q_div.
Result: six singleton blocks, strictly lower triangular. This is exactly the current DAG.
The compiler selects the fast path; performance is unchanged.

**Case B — inverse.** Known: `P_net, q_div (= q_limit), M_blanket, eta_th, f_recirc, f_div`.
Unknown: `P_fusion, P_thermal, P_gross, P_recirc, P_div, A_div`.
Matching: eq3→P_recirc, eq4→P_gross, eq2→P_thermal, eq1→P_fusion, eq5→P_div, eq6→A_div.
Result: eq3 and eq4 form a 2×2 irreducible block (Newton or, here, a trivial linear solve), then
four singletons.

Same model. Same source file. No rewrite. The loop structure in Case B is *discovered by the
compiler*, not authored.

Case B is the question that matters: "design a plant that delivers 500 MWe with the divertor
sitting exactly at its heat flux limit — what fusion power does that require?"

### 4.5 Block dispatch

| Block shape | Solver |
|---|---|
| Singleton, variable in `direct_for` | Symbolic isolation, direct substitution |
| Singleton, not in `direct_for` | Scalar Newton or Brent on the residual |
| Small block, all relations linear in block variables | Direct linear solve (LU) |
| Small–medium block, smooth | Newton with analytic Jacobian; trust region for robustness |
| Poorly scaled or bad initial guess | Homotopy / continuation from a solved neighbor point |
| Contains a tier-4 external call | Newton with finite-difference Jacobian, or surrogate + fixed point. **Cost surfaces to the user.** |

Note the second row: symbolic invertibility is a **performance** property, not a capability
boundary. A relation you cannot isolate algebraically is just a 1×1 Newton block. The real
capability boundary is differentiability (§7).

### 4.6 Uncertainty

Given fusion LCOE estimates spanning roughly $140–550/MWh, propagation of uncertainty is arguably
more valuable than point estimates. Two options, in order of cost:

1. **Interval / affine arithmetic.** If catalog entries carry ranges, this gives rigorous bounds
   cheaply. Affine arithmetic reduces the dependency-driven over-conservatism of naive intervals.
   Requires interval-aware residual evaluation, which the symbolic form supports directly.
2. **Sampling.** Monte Carlo or quasi-MC over the compiled residual system. Straightforward but
   expensive when tier-4 relations are in the loop.

Rigorous bounds may be a more defensible deliverable than a point estimate with error bars nobody
believes.

---

## 5. Failure modes and cautions

**Structural ≠ numerical.** DM sees sparsity only. `x + y = 1` with `2x + 2y = 2` is structurally
square and numerically singular. The decomposition is *necessary but not sufficient*. Check
Jacobian rank at the solve point; the BLT diagonal blocks localize numerical singularity the same
way DM localizes structural singularity.

**Incidence sets must be exact — the principal LLM exposure.** If a generated relation declares
`(a, b, c)` but only uses `a` and `b`, a phantom edge is created. The matcher may then produce a
structurally valid, numerically singular assignment. **Mitigation:** compute the actual Jacobian
sparsity pattern via AD or symbolic differentiation and diff it against the declared incidence.
A mismatch is a model defect with a precise SysML element location. This belongs in the validation
tier stack and is a concrete instance of "the formal model as a compiler for AI-generated content."

**Variable identity is the hard part.** More on this in §6.2.

**Piecewise relations break Newton silently.** Discontinuous derivatives cause cycling that looks
like a solver bug rather than a modeling issue. See §7 tier 2 — this is the most likely source of
mysterious failures in practice.

**Initial guesses matter more than in a DAG.** A forward pass needs none. Newton needs a basin.
Sources, in order of preference: previous solve in a sweep, forward-mode solution of the same
model, catalog-provided nominal values, declared bounds midpoint. Variable `scale` also matters —
mixing quantities of order 10⁹ (watts) and 10⁻³ (fractions) in one Newton block without scaling
produces spurious non-convergence.

**Black boxes inside SCCs are expensive and should be loud.** A tier-4 relation inside an
irreducible block means Newton calls it every iteration. If the external code takes minutes, the
solve takes hours. The compiler should surface this as an explicit warning with a cost estimate and
require the modeler to choose: accept the cost, build a surrogate, or restructure. It must never
be handled silently.

**Scope discipline.** Steady-state algebraic plus external black boxes is a coherent scope.
Admitting ODEs/DAEs means index reduction, consistent initialization, and event handling — Modelica's
problem space, with twenty years of solver hardening M-Scout does not have. Hold the line at
tier 4 (§7).

---

## 6. Impact on extraction

### 6.1 Why extraction gets simpler

The claim is specific: **extraction becomes element-local and stateless.**

Current extraction performs whole-model reasoning: resolve which `calc`'s output feeds which
other `calc`'s input, detect and reject cycles, topologically sort, determine which inputs are
undriven and therefore free. That is bespoke graph code, and it is where ordering bugs live.

Under the relational form, each element maps to a `Relation` record independently of every other
element. Walk the model; emit one record per usage; done.

**Removed from the extractor:**

- DAG edge wiring by name matching
- Topological sort
- Cycle detection and rejection
- Undriven-input analysis
- Divergent code paths for `calc` vs `constraint`

**Added to the extractor:**

- Incidence set — the free symbols of the residual expression. *Cheaper* than the current wiring
  logic, because it is a local property rather than a cross-element name-resolution pass.
- `solvable_for` / `direct_for` — roughly one predicate per tier (see Appendix B).

**Moved out of the extractor:** all global reasoning, into a compile pass built on published
algorithms with known complexity rather than hand-rolled graph code.

**The executor barely changes.** It executes a block sequence instead of a statement sequence,
where in the common case every block is a singleton.

### 6.2 What gets harder: variable identity

This is the one genuine cost, and it should be planned for rather than discovered.

The current DAG resolves identity implicitly through wiring. In the relational form, two relations
share a variable if and only if they emit the **same qualified name**. Consequences:

- Extraction must walk **usages**, not definitions. `PowerBalance` used three times is three
  relations with three distinct variable sets.
- Parameter names must be qualified by usage path: `plant.blanket.thermalPower`, not
  `thermalPower`.
- Bind-through and connections (`plant.blanket.P_out = plant.turbine.P_in`) must either emit an
  explicit identity relation or be union-found into a single canonical name. Union-find is
  preferred — it keeps the matrix smaller — but the alias map must be retained for diagnostics, so
  errors report the name the author wrote.

Getting this wrong produces a structurally under-determined system where a square one was
expected. The symptom is DOF appearing from nowhere. Budget debugging time here.

### 6.3 Migration path

Incremental, with a regression guard at each step:

1. Add the `Relation` dataclass and normalization functions alongside the existing extractor.
   Emit both representations. No behavior change.
2. Build the compile pass. On existing models it should produce all-singleton blocks in the same
   topological order as the current DAG. **This is the regression test:** compiled order must match
   DAG order on every existing model.
3. Switch the executor to consume blocks. Singleton blocks execute exactly as today.
4. Add Newton dispatch for non-singleton blocks. Algebraic loops now work.
5. Add analysis-case partitioning. Inverse solve now works.
6. Add DOF reporting and optimizer handoff.
7. Add the incidence-vs-Jacobian validation check.

Steps 1–3 are pure refactor with no user-visible change. Value appears at step 4.

### 6.4 Codegen implications

Bias the LLM comment-block generator toward emitting **symbolic expressions** (SysML expression
syntax, or SymPy) rather than Python source, falling back to opaque code only when it genuinely
cannot. Every block moved from tier 4 to tier 0/1 gains:

- invertibility,
- exact derivatives,
- unit checking,
- eligibility for the catalog.

A symbolic relation with declared units and a validity range is a reusable asset. A Python blob is
a leaf node someone has to trust. This is the same argument as the catalog thesis, applied at the
level of a single generated function.

---

## 7. Tier classification

The governing question per relation is not "is this expressible?" but "what can the compiler do
with it?" Three capabilities: **evaluate**, **differentiate**, **invert**.

| Tier | Math | Evaluate | Differentiate | `solvable_for` |
|---|---|---|---|---|
| **0** Algebraic | Closed-form; each variable appears once, linearly | ✓ | analytic | all variables, direct substitution |
| **1** Implicit | Variable appears multiple times; transcendental (Colebrook, Antoine, Blasius) | ✓ | AD | all variables, flagged iterative |
| **2** Piecewise | `if`/`else`, `min`/`max`, clamps, regime switches | ✓ | discontinuous | restricted — see below |
| **3** Tabulated | Interpolated catalog data: material properties, pump curves | ✓ | ✓ if C¹ interpolation | independent variable only if monotone |
| **4** External | Neutronics, CFD, CAD, opaque generated code | expensive | finite-diff or none | `{output}` only |
| **5** Out of scope | ODE/PDE, discrete choice, combinatorial | — | — | not admitted |

**Tiers 0–1** are the bulk of TEA mathematics and need no annotation — the classifier infers them.

**Tier 2 is the one that will bite.** Engineering models are saturated with conditionals: part-load
efficiency curves, properties that switch at a phase boundary, cost correlations valid only above a
size threshold. They evaluate correctly forward, which is why the current DAG has been untroubled
by them. Under Newton they cause cycling and spurious non-convergence. Three resolutions, and the
modeler must choose explicitly:

- **Pin forward-only** — exclude the switching variable from `solvable_for`.
- **Smooth** — tanh or log-sum-exp blend with a *declared* width, so the approximation is visible.
- **Reformulate as complementarity** — if the downstream optimizer supports it (MPCC).

**Tier 3 is where the catalog thesis becomes mechanical.** A catalog entry *is* a relation:
tabulated data, validity range, provenance, interpolation scheme. Use monotone C¹ interpolation
(PCHIP, not linear) and the independent variable remains in `solvable_for` — meaning "what inlet
temperature would I need for this enthalpy change?" works against a property table with nobody
having authored an inverse.

**Tier 4 is the escape hatch, and should be treated as a cost center.** Every relation promoted out
of tier 4 improves the model's tractability.

---

## Appendix A — SysML v2 expression

*Caveat: SysML v2 tooling and syntax remain in flux. The metadata and conditional-expression forms
below should be validated against the current pilot implementation before committing to them.*

### A.1 The solver hint annotation

Tiers are primarily *inferred*. Annotation is needed only where inference cannot reach — chiefly
tier 2 smoothing choices and tier 4 declarations.

```sysml
metadata def SolverHint {
    attribute tier            : Integer;   // 0..4, overrides inference
    attribute cost            : String;    // "free" | "seconds" | "minutes"
    attribute invertible      : Boolean;   // false ⇒ solvable_for = {output}
    attribute smoothing       : String;    // "none" | "tanh" | "logsumexp"
    attribute smoothingWidth  : Real;
}

metadata def CatalogRef {
    attribute source        : String;      // provenance — required
    attribute material      : String;
    attribute validRange    : String;
    attribute interpolation : String;      // "pchip" | "linear" | "spline"
    attribute monotone      : Boolean;
}
```

### A.2 Tier 0 — algebraic, no annotation

```sysml
calc def GrossElectric {
    in P_thermal : PowerValue;
    in eta_th    : Real;
    return P_gross : PowerValue = P_thermal * eta_th;
}
```

Inferred tier 0. `solvable_for = {P_gross, P_thermal, eta_th}` — all three isolable, so this
element supports inverse solve with no extra authoring.

### A.3 Tier 1 — implicit, use `constraint def`

This is the case that argues for `constraint def` beyond limit enforcement:

```sysml
constraint def ColebrookFriction {
    in f        : Real;
    in Re       : Real;
    in relRough : Real;

    1 / sqrt(f) == -2 * log10(relRough / 3.7 + 2.51 / (Re * sqrt(f)))
}
```

`f` appears on both sides. No `calc def` can express this without hand-derived iteration. The
extractor detects multiple occurrence, classifies tier 1, and keeps `f` in `solvable_for` flagged
as iterative.

### A.4 Tier 2 — piecewise, annotation required

```sysml
@SolverHint { tier = 2; smoothing = "tanh"; smoothingWidth = 0.02; }
calc def PartLoadEfficiency {
    in loadFraction : Real;
    in etaNominal   : Real;
    return : Real =
        if loadFraction >= 0.5 ? etaNominal * (0.90 + 0.10 * loadFraction)
        else etaNominal * (0.60 + 0.70 * loadFraction);
}
```

The extractor finds `loadFraction` in a branch condition. Without the smoothing declaration it
would be removed from `solvable_for`. The annotation exists because *which* resolution to apply is
a modeling judgment, not something to infer.

### A.5 Tier 3 — catalog-backed, body-less

```sysml
@CatalogRef {
    source        = "NIST SRD 155";
    material      = "SS316L";
    validRange    = "300..900";     // K
    interpolation = "pchip";
    monotone      = true;
}
calc def SS316L_ThermalConductivity {
    in T : TemperatureValue;
    return k : Real;
}
```

No body. The extractor resolves against the catalog. Because the entry declares monotone PCHIP,
`T` remains in `solvable_for` — so `k` known, `T` unknown works directly.

### A.6 Tier 4 — external

```sysml
@SolverHint { tier = 4; cost = "minutes"; invertible = false; }
calc def TritiumBreedingRatio {
    in blanketThickness : LengthValue;
    in liEnrichment     : Real;
    return TBR : Real;
}
```

### A.7 Limits stay where they are

```sysml
requirement def DivertorHeatFluxLimit {
    subject d : Divertor;
    attribute q_peak  : Real;
    attribute q_limit : Real;
    require constraint { q_peak <= q_limit }
}
```

Requirements become the inequality set. DM's over-determined block is then, precisely,
*"your requirements exceed your available freedom."*

### A.8 Analysis case owns the partition

```sysml
analysis case def InverseSizing {
    subject plant : FusionPlant;

    // known set — the question being asked
    in P_net_target : PowerValue = 500 [MW];
    in q_div_target : Real = 10.0;      // at the divertor limit

    objective { minimize plant.lcoe }
}
```

This is the construct that should own the known/unknown partition, the objective, and the fidelity
budget. It is instantiated per question; the model is not.

### A.9 Construct mapping summary

| SysML v2 construct | Normalization |
|---|---|
| `calc def` returning `e`, output `y` | residual `y − e`; `y` forced into `solvable_for` |
| `constraint def` with top-level `==` | residual `lhs − rhs`; `solvable_for` = isolable set |
| `constraint def` with `<`, `<=`, `>`, `>=` | inequality; excluded from matching |
| Conjunction (`and`) | split into separate relations |
| Disjunction (`or`) | do not decompose; treat as opaque check |
| `requirement def` + `require constraint` | inequality set / viability constraints |
| `analysis case def` | known/unknown partition, objective, fidelity budget |
| ISQ / SI unit attributes | dimensional consistency pre-pass |
| Bind / connect | union-find into canonical variable name; retain alias map |

---

## Appendix B — Python primitive and extraction

### B.1 The `Relation` dataclass

```python
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Optional
import sympy as sp


class Tier(IntEnum):
    ALGEBRAIC = 0
    IMPLICIT  = 1
    PIECEWISE = 2
    TABULATED = 3
    EXTERNAL  = 4


@dataclass(frozen=True)
class Relation:
    id: str
    source: str                        # SysML qualified name — for diagnostics
    kind: str                          # "eq" | "ineq"
    tier: Tier
    vars: frozenset[str]               # exact incidence set
    solvable_for: frozenset[str]       # admissible matches
    direct_for: frozenset[str]         # subset solvable in closed form
    residual: Optional[sp.Expr]        # r(x) = 0; None for tier 4
    evaluate: Optional[Callable]       # opaque fallback
    cost: str
    validity: dict

    def isolate(self, var: str) -> Optional[sp.Expr]:
        """Closed-form solution for `var`, or None if not directly isolable."""
        if var not in self.direct_for:
            return None
        sols = sp.solve(self.residual, sp.Symbol(var), dict=False)
        return sols[0] if len(sols) == 1 else None
```

### B.2 Extraction from a `calc` usage

```python
def from_calc(usage, scope) -> Relation:
    out  = qualify(scope, usage.return_param)        # usage path, not param name
    body = translate(usage.definition.body, scope)   # SysML expr -> sympy
    hint = read_metadata(usage, "SolverHint")

    if hint.get("tier") == 4 or body is None:
        return Relation(
            id=usage.id,
            source=qualified_name(usage),
            kind="eq",
            tier=Tier.EXTERNAL,
            vars=frozenset([out]) | inputs(usage, scope),
            solvable_for=frozenset([out]),
            direct_for=frozenset([out]),
            residual=None,
            evaluate=bind_external(usage),
            cost=hint.get("cost", "seconds"),
            validity=read_validity(usage),
        )

    residual     = sp.Symbol(out) - body
    tier         = classify(residual, hint)
    solv, direct = admissible(residual, tier, hint, forced_out=out)

    return Relation(
        id=usage.id,
        source=qualified_name(usage),
        kind="eq",
        tier=tier,
        vars=frozenset(map(str, residual.free_symbols)),
        solvable_for=solv,
        direct_for=direct,
        residual=residual,
        evaluate=None,
        cost="free",
        validity=read_validity(usage),
    )
```

### B.3 Extraction from a `constraint` usage

Nearly identical. The only differences are residual construction and the absence of a forced
output:

```python
def from_constraint(usage, scope) -> Relation:
    expr = translate(usage.definition.expr, scope)

    if isinstance(expr, sp.Equality):
        residual, kind = expr.lhs - expr.rhs, "eq"
    else:                                          # <, <=, >, >=
        residual, kind = as_slack(expr), "ineq"    # g(x) <= 0 convention

    hint = read_metadata(usage, "SolverHint")
    tier = classify(residual, hint)

    if kind == "ineq":
        solv, direct = frozenset(), frozenset()    # excluded from matching
    else:
        solv, direct = admissible(residual, tier, hint)

    return Relation(
        id=usage.id,
        source=qualified_name(usage),
        kind=kind,
        tier=tier,
        vars=frozenset(map(str, residual.free_symbols)),
        solvable_for=solv,
        direct_for=direct,
        residual=residual,
        evaluate=None,
        cost="free",
        validity=read_validity(usage),
    )
```

That the two functions are this similar is the point — the `calc` / `constraint` distinction
survives only as a difference in `solvable_for`, not as a difference in kind.

### B.4 Classification

```python
def switching_vars(expr) -> set[str]:
    """Variables whose value selects a branch — these break differentiability."""
    s = set()
    for pw in expr.atoms(sp.Piecewise):
        for _, cond in pw.args:
            if cond is not sp.true:
                s |= {str(x) for x in cond.free_symbols}
    for f in (sp.Min, sp.Max, sp.Abs, sp.floor, sp.ceiling):
        for node in expr.atoms(f):
            s |= {str(x) for x in node.free_symbols}
    return s


def classify(residual, hint) -> Tier:
    if "tier" in hint:
        return Tier(hint["tier"])
    if switching_vars(residual):
        return Tier.PIECEWISE
    for sym in residual.free_symbols:
        if residual.count(sym) > 1:
            return Tier.IMPLICIT
    return Tier.ALGEBRAIC


def admissible(residual, tier, hint, forced_out=None):
    """Return (solvable_for, direct_for)."""
    if tier is Tier.PIECEWISE and hint.get("smoothing", "none") == "none":
        blocked = switching_vars(residual)
    else:
        blocked = set()

    solv, direct = set(), set()
    for sym in residual.free_symbols:
        name = str(sym)
        if name in blocked:
            continue
        if residual.diff(sym) == 0:        # phantom: declared but unused
            continue
        solv.add(name)
        if residual.count(sym) == 1 and sp.degree(residual, sym) == 1:
            direct.add(name)

    if hint.get("invertible") is False and forced_out:
        solv, direct = {forced_out}, {forced_out}

    return frozenset(solv), frozenset(direct)
```

Three things worth noting:

- `residual.diff(sym) == 0` is the **phantom-variable check**, falling out for free on symbolic
  relations. Declared-but-unused parameters are dropped from the incidence set rather than creating
  a spurious edge. This is the primary defense against LLM-generated incidence errors.
- `direct_for` is what lets the executor use substitution on a singleton block instead of invoking
  Newton — i.e. how the current fast path survives.
- `invertible = false` is the escape hatch for cases where the author knows something the symbolic
  layer does not.

### B.5 Compile pass sketch

```python
import numpy as np
import scipy.sparse as sps
from scipy.sparse.csgraph import maximum_bipartite_matching, connected_components


def compile_case(relations, known: set[str]):
    eqs      = [r for r in relations if r.kind == "eq"]
    ineqs    = [r for r in relations if r.kind == "ineq"]
    unknowns = sorted({v for r in eqs for v in r.vars} - known)
    vidx     = {v: j for j, v in enumerate(unknowns)}

    rows, cols = [], []
    for i, r in enumerate(eqs):
        for v in r.solvable_for - known:
            rows.append(i)
            cols.append(vidx[v])
    A = sps.coo_matrix(
        (np.ones(len(rows)), (rows, cols)),
        shape=(len(eqs), len(unknowns)),
    ).tocsr()

    match = maximum_bipartite_matching(A, perm_type="column")

    dof     = len(unknowns) - int((match >= 0).sum())
    excess  = len(eqs) - int((match >= 0).sum())

    if dof > 0:
        return UnderDetermined(dof=dof, free_candidates=..., ineqs=ineqs)
    if excess > 0:
        return OverDetermined(conflicting=..., ineqs=ineqs)

    blocks = block_lower_triangular(eqs, unknowns, match)   # Tarjan SCC + topo sort
    return SolvePlan(blocks=blocks, checks=ineqs)
```

For production, prefer Pyomo's implementation over hand-rolling. Its
`IncidenceGraphInterface.dulmage_mendelsohn()` returns partitions directly, and it is battle-tested
on large chemical process models — a domain with the same structural characteristics as plant-level
TEA. <cite index="1-1">The Dulmage-Mendelsohn partition is used to identify sources of structural singularity, while block triangularization identifies numeric singularity and poor conditioning.</cite> That
pairing is the diagnostic story worth building the UX around.

### B.6 Library options

| Need | Options |
|---|---|
| Matching | `scipy.sparse.csgraph.maximum_bipartite_matching`; `networkx.algorithms.bipartite.hopcroft_karp_matching` |
| DM partition | `pyomo.contrib.incidence_analysis.dulmage_mendelsohn`; hand-roll from Pothen & Fan |
| SCC / BLT | `scipy.sparse.csgraph.connected_components(connection='strong')`; `pyomo...block_triangularize` |
| Symbolic | SymPy (extraction, isolation); SymEngine for speed |
| AD + solve | CasADi (rootfinder, IPOPT interface, sparse AD); JAX (`jax.jacfwd`, `jaxopt`) |
| Newton | `scipy.optimize.root` (hybr, lm); CasADi `rootfinder` for sparse |
| Optimization | IPOPT via Pyomo or CasADi |
| Interval arithmetic | `mpmath.iv`; `python-flint` |

### B.7 The diagnostic layer

The graph algorithms are not the hard part. The hard part is provenance: mapping block-level
findings back to SysML element names so the user reads

> **Over-determined:** `PowerBalance::netPowerConstraint` and `DivertorLimit::heatFluxConstraint`
> are both binding over `{plant.P_fusion, plant.divertor.area}`. Release one specification, or
> promote one to a design variable.

rather than

> `rows [3, 7], cols [2, 5]`

Every `Relation` therefore carries `source`, and the union-find alias map from §6.2 must be
retained so variables report the name the author wrote. **This translation layer is what makes it a
product rather than a solver.**

---

## Appendix C — Open questions

1. **Tearing.** Is it needed for models of the size in play? A 10×10 Newton block is cheap; a
   200×200 block with expensive residuals is not. Defer until a real model demands it.
2. **Where does the analysis case live?** SysML v2 `analysis case def` is the natural home, but
   tooling support should be verified before committing.
3. **Catalog interface.** How does a tier-3 relation resolve its data at compile time? External
   store, embedded, or resolved-and-cached? Affects reproducibility and provenance.
4. **Multi-fidelity dispatch.** Same relation, several implementations at different cost/accuracy;
   the analysis case declares a budget and the dispatcher selects. Maps plausibly onto SysML v2
   redefinition semantics — unverified.
5. **Discrete choices.** Material selection, topology selection. Currently tier 5 / out of scope.
   Admitting them means MINLP.
6. **Interval arithmetic through tier 4.** External codes do not accept intervals. Surrogate with
   error bounds, or sample?
7. **Guess propagation across a sweep.** Reusing the previous point's solution is the standard
   trick; needs a place in the executor's state model.

---

## Appendix D — Self-critique

**Where this report is confident:**

- The DM / BLT pipeline is standard, well-documented, and implemented in multiple mature systems.
  The algorithmic claims are not novel and are unlikely to be wrong.
- The claim that the current DAG is a special case of the relational scheme is structurally true,
  which is what makes the migration additive rather than a rewrite.
- The tier classification maps onto real capability boundaries (evaluate / differentiate / invert).

**Where it is uncertain:**

- **SysML v2 syntax.** Metadata definitions, conditional expression syntax, and `analysis case def`
  semantics are given from general knowledge of the specification, not verified against current
  tooling. Validate before implementing.
- **Effort estimate.** "~200 lines" covers the graph algorithms only. Variable identity resolution
  (§6.2) and the diagnostic layer (B.7) are the majority of the work and are not estimated here.
- **Whether tier 2 is as common in fusion TEA as claimed.** Asserted from general engineering
  modeling experience; should be checked against the actual `fusion-tea` model corpus by counting
  conditionals.
- **Numerical robustness at scale.** Newton on a poorly scaled 50×50 block with mixed units and
  external calls is where equation-oriented tools historically become painful. This report describes
  the structural machinery, which is the easy half.

**The strongest counterargument:** for models where every relation is a genuine one-way function
and the only need is forward evaluation plus sensitivities, forward-mode AD over the existing DAG
delivers most of the value at a small fraction of the complexity. The relational form should be
justified by *specific inverse and DOF questions that are actually being asked*, not adopted on
general principle. Fusion TEA appears to clear that bar. Other target domains — construction tech
in particular — should be checked separately rather than assumed.

**What would falsify the approach:** if, after implementation, the compiled block structure on real
models is all-singleton in every analysis case anyone actually runs, the machinery is dead weight
and the correct answer was AD over the DAG. Worth checking early — count the SCCs on the existing
`fusion-tea` corpus under a handful of plausible inverse partitions before building step 4 of the
migration.
