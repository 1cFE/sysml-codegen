# Expression Compiler Algorithm Diagram

**Module:** `extraction/expression_compiler.py`
**Context:** EXPR-CODEGEN Item 3

---

## High-Level Data Flow

```
                        CalculationDefinitionData
                        (.input_attributes, .output_attributes)
                                    |
                                    v
   +-------------------------------------------------------------------+
   |                      compile_calc_def()                           |
   |                        (orchestrator)                             |
   |                                                                   |
   |  expression_asts: dict[str, syside_node]                         |
   |  all_member_names: set[str]                                       |
   |  member_expressions: dict[str, syside_node]                       |
   |                                                                   |
   |  1. Build name sets                                               |
   |  2. Build dependency graph  ─── extract_feature_refs() ──┐       |
   |  3. Topological sort (Kahn's)                             │       |
   |  4. For each in topo order:                               │       |
   |     ┌──────────────────────────────────────────────┐      │       |
   |     │  build_expression_ast()  ──> ExpressionAST   │      │       |
   |     │  compile_expression()    ──> Python string   │      │       |
   |     │  _collect_refs()         ──> input/interm.   │      │       |
   |     └──────────────────────────────────────────────┘      │       |
   |  5. classify_compilability()                              │       |
   |                                                    agentic-mbse   |
   +-------------------------------------------------------------------+
                                    |
                                    v
                        CalcDefCompilationResult
                        (.overall_compilability, .output_results,
                         .execution_order)
```

---

## Phase 1: `build_expression_ast()` — syside AST to ExpressionAST IR

Converts opaque syside AST nodes into a clean, testable binary tree IR.
The key transformation is **n-ary to binary left-folding**.

```
INPUT: syside AST node (duck-typed)
       input_names: set[str]
       output_names: set[str]
       all_member_names: set[str] | None

                         syside_node
                              |
                    +---------+---------+
                    |  is_instance()?   |
                    +---------+---------+
                              |
            +-----------------+-------------------+------------------+
            |                 |                   |                  |
      OperatorExpr     FeatureRefExpr      Literal*           Other/Chain
            |                 |                   |                  |
            v                 v                   v                  v
     check operator     extract name         node.value        UNSUPPORTED
            |           _sanitize_name()          |            (raw_text,
            |                 |                   |             reason)
   +--------+--------+       v                   v
   |        |        |  classify name:       LITERAL(value)
   |        |        |  ┌─ in input_names? ──> INPUT_REF(name)
   |        |        |  ├─ in output_names? ─> INTERMEDIATE_REF(name)
   |        |        |  ├─ in member_names? ─> INTERMEDIATE_REF(name)
   |        |        |  └─ else ────────────> UNSUPPORTED("unresolved")
   |        |        |
   v        v        v
 "[" op   1 opnd   2 opnds       >2 opnds (N-ARY LEFT-FOLD)
   |        |        |                  |
   v        v        v                  v
 strip    UNARY    BINARY          see below
 unit     (-x)    (L op R)
 recur
 on [0]


N-ARY LEFT-FOLD (e.g., a + b + c + d):
=========================================

  syside: OperatorExpression("+", [a, b, c, d])

  Step 1: acc = recurse(a)
  Step 2: acc = BINARY("+", acc, recurse(b))    =>  (a + b)
  Step 3: acc = BINARY("+", acc, recurse(c))    =>  ((a + b) + c)
  Step 4: acc = BINARY("+", acc, recurse(d))    =>  (((a + b) + c) + d)

  Result: nested binary tree, left-associative

  Real example — NetElectricPower.p_parasitic_total (7 inputs):
  syside:  OperatorExpression("+", [p1, p2, p3, p4, p5, p6, p7])
  output:  ((((((p1 + p2) + p3) + p4) + p5) + p6) + p7)


OPERATOR MAPPING:
==================
  "+"  -->  " + "     (addition)
  "-"  -->  " - "     (subtraction / unary negation)
  "*"  -->  " * "     (multiplication)
  "/"  -->  " / "     (division)
  "**" -->  " ** "    (power)
  "^"  -->  " ** "    (SysML power alias)
  "["  -->  [strip]   (unit annotation: use value, drop unit)
```

---

## Phase 2: `compile_expression()` — ExpressionAST IR to Python string

Pure recursive descent on the binary tree. No syside dependency.

```
INPUT:  ExpressionAST (binary tree)
OUTPUT: Python expression string

  ExpressionAST
       |
       +-- BINARY_OP(op, left, right)  -->  "({compile(left)}{op}{compile(right)})"
       |
       +-- UNARY_OP("-", operand)      -->  "(-{compile(operand)})"
       |
       +-- LITERAL(value)              -->  str(value)
       |                                    e.g., "3.14159", "17.58", "0.2"
       |
       +-- INPUT_REF(name)             -->  "inputs.{name}"
       |                                    e.g., "inputs.wattage"
       |
       +-- INTERMEDIATE_REF(name)      -->  "{name}"
       |                                    e.g., "material_cost" (bare local var)
       |
       +-- UNSUPPORTED                 -->  raises CompilationError


VALIDATION: ast.parse(result, mode="eval") after every compilation.
            Catches malformed output (unbalanced parens, etc.) at source.


Example — CRF (Capital Recovery Factor) formula:

  ExpressionAST:
    BINARY(/)
    ├── BINARY(*)
    │   ├── INPUT_REF("discount_rate")
    │   └── BINARY(**)
    │       ├── BINARY(+)
    │       │   ├── LITERAL(1.0)
    │       │   └── INPUT_REF("discount_rate")
    │       └── INPUT_REF("plant_lifetime")
    └── BINARY(-)
        ├── BINARY(**)
        │   ├── BINARY(+)
        │   │   ├── LITERAL(1.0)
        │   │   └── INPUT_REF("discount_rate")
        │   └── INPUT_REF("plant_lifetime")
        └── LITERAL(1.0)

  Python output:
    "((inputs.discount_rate * ((1.0 + inputs.discount_rate) ** inputs.plant_lifetime))
     / (((1.0 + inputs.discount_rate) ** inputs.plant_lifetime) - 1.0))"
```

---

## Orchestrator: `compile_calc_def()` — Full CalcDef Compilation

### Step 1: Build Name Sets

```
calc_def.input_attributes  --> input_names:  {"wattage", "cost_per_watt", ...}
calc_def.output_attributes --> output_names: {"material_cost", "fab_cost", "total_cost"}
```

### Step 2: Build Dependency Graph (with undeclared intermediate discovery)

```
For each output (and discovered undeclared intermediate):
  1. Get syside AST from expression_asts or member_expressions
  2. Call extract_feature_refs(ast) --> list of referenced names
  3. Classify each ref:
     - ref in input_names?   --> skip (external input, not a dep edge)
     - ref in output_names?  --> add dependency edge
     - ref in member_names   --> UNDECLARED INTERMEDIATE: add new graph node
       (not in inputs/outputs)  and recurse to discover its deps too

Example — MagnetCryogenicLoad (4 undeclared intermediates):

  Declared outputs: [cryogenic_load]
  Discovered members: [thermal_load_cryo, pump_power_per_unit, thermal_load, ...]

  Pass 1: cryogenic_load refs --> thermal_load_cryo (undeclared!)
  Pass 2: thermal_load_cryo refs --> pump_power_per_unit (undeclared!)
  Pass 3: pump_power_per_unit refs --> thermal_load (undeclared!)
  Pass 4: thermal_load refs --> [inputs only, no more undeclared]

  Final dependency graph:
    cryogenic_load      --> {thermal_load_cryo}
    thermal_load_cryo   --> {pump_power_per_unit}
    pump_power_per_unit --> {thermal_load}
    thermal_load        --> {}  (leaf: depends only on inputs)
```

### Step 3: Topological Sort (Kahn's Algorithm)

```
dep_graph = {
  "total_cost":    {"material_cost", "fab_cost"},
  "fab_cost":      {"material_cost"},
  "material_cost": {},
}

KAHN'S ALGORITHM:
  1. Compute in-degrees (count of graph-internal deps):
     material_cost: 0    fab_cost: 1    total_cost: 2

  2. Initialize queue with in-degree 0 nodes: [material_cost]
     (sorted for deterministic ordering)

  3. Process queue:
     ┌─────────────────────────────────────────────────────────┐
     │ Pop: material_cost                                      │
     │ Result: [material_cost]                                 │
     │ Decrement dependents:                                   │
     │   fab_cost: 1→0  (add to queue)                        │
     │   total_cost: 2→1                                       │
     │                                                         │
     │ Pop: fab_cost                                           │
     │ Result: [material_cost, fab_cost]                       │
     │ Decrement dependents:                                   │
     │   total_cost: 1→0  (add to queue)                      │
     │                                                         │
     │ Pop: total_cost                                         │
     │ Result: [material_cost, fab_cost, total_cost]           │
     └─────────────────────────────────────────────────────────┘

  4. len(result) == len(graph)? YES --> valid ordering
     If NO --> circular dependency detected --> MANUAL_REQUIRED

  execution_order = ["material_cost", "fab_cost", "total_cost"]
```

### Step 4: Compile Each Output in Topological Order

```
For each name in execution_order:

  ┌─ Get AST ──────────────────────────────────────────────────────────┐
  │  Declared output?  --> expression_asts[name]                       │
  │  Undeclared interm.? --> member_expressions[name]                   │
  │  No AST available? --> CompilationResult(MANUAL_REQUIRED)          │
  └────────────────────────────────────────────────────────────────────┘
            |
            v
  ┌─ Build IR ─────────────────────────────────────────────────────────┐
  │  build_expression_ast(syside_node, input_names, output_names,      │
  │                       all_member_names)                             │
  │  --> ExpressionAST (binary tree)                                   │
  └────────────────────────────────────────────────────────────────────┘
            |
            v
  ┌─ Compile to Python ────────────────────────────────────────────────┐
  │  compile_expression(ast)                                           │
  │  --> "material_cost = (inputs.wattage * inputs.cost_per_watt)"     │
  │                                                                    │
  │  On CompilationError (UNSUPPORTED node):                           │
  │  --> CompilationResult(MANUAL_REQUIRED, unsupported_reason=...)     │
  └────────────────────────────────────────────────────────────────────┘
            |
            v
  ┌─ Collect Refs ─────────────────────────────────────────────────────┐
  │  _collect_refs(ast)                                                │
  │  --> (["wattage", "cost_per_watt"], [])    # inputs, intermediates │
  │  Deduplicated, order-preserving (pre-order traversal)              │
  └────────────────────────────────────────────────────────────────────┘
            |
            v
  CompilationResult(
      output_name="material_cost",
      compilability=FULLY_COMPILABLE,
      python_expression="(inputs.wattage * inputs.cost_per_watt)",
      input_refs=["wattage", "cost_per_watt"],
      intermediate_refs=[],
      is_undeclared_intermediate=False,
  )
```

### Step 5: Classify Overall Compilability

```
classify_compilability(output_results):

  Assert: no UNKNOWN values (sentinel misuse guard)

  ALL results FULLY_COMPILABLE?  --> FULLY_COMPILABLE
  ANY result MANUAL_REQUIRED?    --> MANUAL_REQUIRED
  Otherwise (mix of FULLY+PARTIAL) --> PARTIALLY_COMPILABLE
  Empty list?                    --> MANUAL_REQUIRED
```

### Step 6: Return Aggregate Result

```
CalcDefCompilationResult(
    calc_def_name = "CostEstimator",
    overall_compilability = FULLY_COMPILABLE,
    output_results = [
        CompilationResult("material_cost", FULLY, "(inputs.wattage * inputs.cost_per_watt)", ...),
        CompilationResult("fab_cost", FULLY, "(material_cost * inputs.fab_multiplier)", ...),
        CompilationResult("total_cost", FULLY, "(material_cost + fab_cost)", ...),
    ],
    execution_order = ["material_cost", "fab_cost", "total_cost"],
)

NOTE: execution_order includes undeclared intermediates.
      is_undeclared_intermediate flag on CompilationResult tells the
      generator which names go in the return statement (declared only)
      vs. which are local variable assignments only.
```

---

## End-to-End Example: Pattern B (Multi-Step Cost Estimation)

```
SysML CalcDef: CostEstimator
  inputs:  wattage, cost_per_watt, fab_multiplier
  outputs: material_cost, fab_cost, total_cost

  material_cost = wattage * cost_per_watt
  fab_cost      = material_cost * fab_multiplier
  total_cost    = material_cost + fab_cost


STEP 1: Name Sets
  input_names  = {"wattage", "cost_per_watt", "fab_multiplier"}
  output_names = {"material_cost", "fab_cost", "total_cost"}


STEP 2: Dependency Graph
  extract_feature_refs(material_cost_ast) --> [wattage, cost_per_watt]
    wattage in input_names --> skip
    cost_per_watt in input_names --> skip
    deps = {}

  extract_feature_refs(fab_cost_ast) --> [material_cost, fab_multiplier]
    material_cost in output_names --> dep edge!
    fab_multiplier in input_names --> skip
    deps = {material_cost}

  extract_feature_refs(total_cost_ast) --> [material_cost, fab_cost]
    material_cost in output_names --> dep edge!
    fab_cost in output_names --> dep edge!
    deps = {material_cost, fab_cost}

  Graph:
    material_cost --> {}
    fab_cost      --> {material_cost}
    total_cost    --> {material_cost, fab_cost}


STEP 3: Topological Sort
  In-degrees: material_cost=0, fab_cost=1, total_cost=2
  Order: [material_cost, fab_cost, total_cost]


STEP 4: Compile Each

  material_cost:
    syside AST: OperatorExpression("*", [FeatureRef("wattage"), FeatureRef("cost_per_watt")])
    --> build_expression_ast:
        BINARY("*", INPUT_REF("wattage"), INPUT_REF("cost_per_watt"))
    --> compile_expression:
        "(inputs.wattage * inputs.cost_per_watt)"

  fab_cost:
    syside AST: OperatorExpression("*", [FeatureRef("material_cost"), FeatureRef("fab_multiplier")])
    --> build_expression_ast:
        BINARY("*", INTERMEDIATE_REF("material_cost"), INPUT_REF("fab_multiplier"))
    --> compile_expression:
        "(material_cost * inputs.fab_multiplier)"

  total_cost:
    syside AST: OperatorExpression("+", [FeatureRef("material_cost"), FeatureRef("fab_cost")])
    --> build_expression_ast:
        BINARY("+", INTERMEDIATE_REF("material_cost"), INTERMEDIATE_REF("fab_cost"))
    --> compile_expression:
        "(material_cost + fab_cost)"


STEP 5: Classify
  All 3 FULLY_COMPILABLE --> overall = FULLY_COMPILABLE


GENERATED FUNCTION BODY (Item 4 will emit this):
  material_cost = (inputs.wattage * inputs.cost_per_watt)
  fab_cost = (material_cost * inputs.fab_multiplier)
  total_cost = (material_cost + fab_cost)
  return (material_cost, fab_cost, total_cost)
```

---

## Reference Name Resolution Flow

```
syside FeatureReferenceExpression
         |
         v
expression_utils.extract_feature_reference_name()
  (shared utility, from constraint_extractor refactor)
  accesses: .referent.name, .memberships, .declared_name, .name
         |
         v
_sanitize_name()
  (expression_compiler private helper)
  strips quotes, replaces spaces with underscores
  matches extractor._sanitize_name() convention
         |
         v
    sanitized name: "my_parameter"
         |
    +----+----+----+----+
    |         |         |         |
    v         v         v         v
 in input  in output  in member  else
 _names?   _names?    _names?
    |         |         |         |
    v         v         v         v
 INPUT_REF  INTER-    INTER-   UNSUPPORTED
            MEDIATE   MEDIATE  ("unresolved
            _REF      _REF      reference")
           (declared  (undeclared
            output)   member)
```
