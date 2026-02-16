# Design: AST Dispatch & Resolution Route Cleanup

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-16 17:30 UTC
**Branch:** cost-pattern
**Commit:** 118db97
**Prerequisite:** Aggregation Wiring Bugfix (Bug A + Bug B) must land first

## Overview

Extract a shared AST node classifier to eliminate the dispatch ordering bug class,
and extract shared resolution utilities from the CalcUsage/backtracker and
aggregation paths to reduce duplication.

## Related Artifacts

- **Spec:** `.project/active/ast-dispatch-resolution-cleanup/spec.md`
- **Bugfix spec:** `.project/active/aggregation-wiring-bugfix/spec.md`
- **Spike results:** `.project/active/aggregation-wiring-spikes/plan.md`
- **Algorithm doc:** `.project/reports/08_algorithm_revised.md` (Section 13)

---

## Research Findings

### Dispatch Site Inventory

All 7 sites follow the same structural pattern: "given a SysIDE AST node,
determine its type, then do type-specific work." The type-specific work
varies across sites:

| Site | File:Lines | Returns | What it does per node type |
|------|-----------|---------|---------------------------|
| `_extract_single_redefinition` | hierarchy_resolver.py:94-136 | `RedefinitionData` | Classifies into LITERAL/CHAIN/EXPRESSION |
| `_unwrap_invocation` | hierarchy_resolver.py:278-302 | `Any` (AST node) | Checks for terminal (FCE/FRE=stop, Invocation=keep unwrapping) |
| `_walk_aggregation_ast` | hierarchy_resolver.py:305-433 | `str` (expression text) | Recursive walk: OE=recurse, FCE=SingletonTerm, FRE=LocalTerm, Invocation=sum |
| `reconstruct_expression` | expression_utils.py:34-76 | `str` (text) | OE="left op right", FRE=name, FCE=chain, Invocation="func(args)", Literal=value |
| `build_expression_ast` | expression_compiler.py:290-405 | `ExpressionAST` | OE=binary/unary, FRE=input_ref, Literal=literal, FCE=unsupported |
| `_extract_single_binding` | usage_extractor.py:503-571 | `BindingInfo` | FCE=CHAIN, FRE=REFERENCE, Literal=LITERAL, OE=EXPRESSION |
| `_extract_default_value` | parameter_groups.py:158-199 | `str \| None` | Literal=str(value), FRE=path, FCE=path, OE=evaluate |

**Key observation:** The **only common part** across all 7 sites is
node type identification. The type-specific handlers have completely
different signatures, return types, and logic. Some sites recurse
(walk, reconstruct), others don't. Some need context parameters
(mult_lookup, input_names), others don't.

### SysIDE Type Hierarchy (from Spike A)

SysIDE's `is_instance()` overlaps are:
- `FeatureChainExpression` → matches both `"FeatureChainExpression"` AND `"OperatorExpression"` (it's a subtype)
- `FeatureReferenceExpression` → matches only `"FeatureReferenceExpression"` (not OE)
- `OperatorExpression` → matches only `"OperatorExpression"` (not FCE/FRE)
- `InvocationExpression` → detected by `hasattr(node, "function")`, which also matches FCE and FRE (they carry `function` too)

So the mandatory ordering is:
1. `FeatureChainExpression` — most specific (subtype of OE)
2. `FeatureReferenceExpression` — specific (not OE, but has `function`)
3. `OperatorExpression` — general (catches non-FCE operators)
4. `InvocationExpression` via `hasattr(node, "function")` — most general (catches everything with `function`)
5. Literal types — disjoint from above
6. Unknown — fallback

### `_unwrap_invocation` is a special case

This function uses dispatch differently — it's not dispatching to type-specific
handlers but checking for **terminal conditions** (FCE/FRE = stop) vs.
**continuation** (InvocationExpression = recurse). It never handles OE or
literals. It may or may not benefit from the shared mechanism.

### Resolution Path Comparison

**Common operations (extracted from code):**

| Operation | CalcUsage Path (backtracker.py:455-528) | Aggregation Path (graph_builder.py:740-847) |
|-----------|---------------------------------------|---------------------------------------------|
| Direct registry lookup | `registry.resolve(source_path)` (line 474) | `registry.resolve(scoped_key)` (line 823) |
| Scoped key construction | `f"{parent_part}.{leaf}"` (line 445) | `f"{dotted_scope}.{part_usage}.{attr}"` (line 822) |
| Unscoped key fallback | N/A (uses parent_part directly) | `f"{part_usage}.{attr}"` (line 832) |
| Self-reference guard | `producing_usage_qn != usage.qualified_name` (line 489) | Not implemented |
| Entry point fallback | `f"{usage.qualified_name}__{param_name}"` (line 525) | `f"{agg.module_eqn}__{param_name}"` (line 993/1017) |

**Domain-specific operations (NOT shared):**

| Strategy | Owner | Why it's domain-specific |
|----------|-------|-------------------------|
| CHAIN recursive resolution (with cycle detection) | Aggregation only (graph_builder.py:789-813) | Follows `:>>` CHAIN redefinitions through the hierarchy. Only aggregation inputs reference child PartDef attributes that have CHAIN redefs to CalcUsage outputs. |
| REFERENCE secondary resolution (leaf + parent scope) | CalcUsage only (backtracker.py:422-453) | Handles SYSML_QN source_paths from REFERENCE bindings. Only CalcUsage bindings use SYSML_QN format. |
| Design attribute fallback | CalcUsage only (backtracker.py:530-609) | Resolves to design-file literal values. Aggregation inputs either wire to module outputs or become entry points — no design attribute intermediate. |
| Canonical channel verification | Aggregation only (graph_builder.py:807, 980) | Verifies constructed channel exists in `canonical_channels` set before accepting. Backtracker trusts registry. |

**Actual duplication is narrow:** Both paths call `output_registry.resolve()`
with constructed scoped keys. The key construction differs (different segment
splitting, different prefix stripping), and the fallback chains differ. The
shared operation is: "try resolving a dotted ref via the registry, possibly
with scope prefixing."

---

## Design Alternatives

### Workstream 1: AST Dispatcher API

#### Option A: Classify Function + Enum

A single `classify_ast_node()` function returns an enum value. Each call
site uses the enum to branch into its own type-specific logic.

```python
# core/ast_node_types.py (or extraction/ast_dispatch.py)

from enum import Enum, auto

class ASTNodeKind(Enum):
    """SysIDE AST node classification.

    Ordering is critical — FeatureChainExpression is a subtype of
    OperatorExpression in SysIDE's type system (both is_instance()
    checks return True). This enum encodes the correct classification
    via classify_ast_node(), which checks specific types first.
    """
    FEATURE_CHAIN = auto()       # child.attr dotted reference
    FEATURE_REFERENCE = auto()   # bare name reference
    OPERATOR = auto()            # binary/unary/n-ary operator
    INVOCATION = auto()          # function call (sum, sqrt, etc.)
    LITERAL = auto()             # integer, real, boolean, string, null
    UNKNOWN = auto()             # unrecognized node type

def classify_ast_node(node: Any) -> ASTNodeKind:
    """Classify a SysIDE AST node with correct type ordering.

    This is the SINGLE POINT where dispatch ordering is enforced.
    All AST-walking code MUST use this instead of independent
    is_instance() chains.
    """
    if node is None:
        return ASTNodeKind.UNKNOWN
    # CRITICAL: FCE before OE (FCE is subtype of OE)
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        return ASTNodeKind.FEATURE_CHAIN
    # CRITICAL: FRE before hasattr(function) (FRE has .function too)
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        return ASTNodeKind.FEATURE_REFERENCE
    if SysideAdapter.is_instance(node, "OperatorExpression"):
        return ASTNodeKind.OPERATOR
    if hasattr(node, "function") and hasattr(node.function, "name"):
        return ASTNodeKind.INVOCATION
    if _is_literal(node):
        return ASTNodeKind.LITERAL
    return ASTNodeKind.UNKNOWN

def _is_literal(node: Any) -> bool:
    """Check if a SysIDE AST node is a literal value expression.

    Private to ast_dispatch — avoids circular import with expression_utils.
    Includes NullExpression (which expression_utils.is_literal_expression
    does NOT cover).
    """
    return (
        SysideAdapter.is_instance(node, "LiteralInteger")
        or SysideAdapter.is_instance(node, "LiteralRational")
        or SysideAdapter.is_instance(node, "LiteralReal")
        or SysideAdapter.is_instance(node, "LiteralBoolean")
        or SysideAdapter.is_instance(node, "LiteralString")
        or SysideAdapter.is_instance(node, "NullExpression")
    )
```

Consumer pattern:

```python
kind = classify_ast_node(node)
if kind == ASTNodeKind.FEATURE_CHAIN:
    chain_name = extract_feature_chain_name(node)
    ...
elif kind == ASTNodeKind.OPERATOR:
    operands = list(getattr(node, "operands", []))
    ...
elif kind == ASTNodeKind.UNKNOWN:
    logger.warning("Unrecognized AST node: %s", type(node).__name__)
    ...
```

**Pros:**
- Simple: ~25 lines of new code. Easy to understand and maintain.
- Flexible: each site keeps full control over its type-specific logic,
  recursion, context threading, and return types.
- Natural fit: the 7 sites have wildly different handler signatures and
  behavior. The only thing they share IS the classification.
- Incrementally adoptable: can migrate sites one at a time.
- `_unwrap_invocation` works naturally — just check the kind for its 3 cases.

**Cons:**
- Consumers COULD still forget a case (no compile-time exhaustiveness check).
  Mitigated by: (1) the UNKNOWN case catches unhandled types, (2) unit tests
  cover all 6 enum values, (3) a linter rule or code review convention could
  flag unchecked cases.
- Two-step pattern (classify then branch) is slightly more verbose than direct
  dispatch. But the verbosity makes the logic explicit.

#### Option B: Generic Callback Dispatcher

```python
@dataclass
class ASTHandlers(Generic[T]):
    on_feature_chain: Callable[[Any], T]
    on_feature_reference: Callable[[Any], T]
    on_operator: Callable[[Any], T]
    on_invocation: Callable[[Any], T]
    on_literal: Callable[[Any], T]
    on_unknown: Callable[[Any], T]

def dispatch_ast_node(node: Any, handlers: ASTHandlers[T]) -> T:
    kind = classify_ast_node(node)
    handler = {
        ASTNodeKind.FEATURE_CHAIN: handlers.on_feature_chain,
        ...
    }[kind]
    return handler(node)
```

**Pros:**
- Exhaustive by construction: all 6 handlers must be provided.
- Single dispatch call replaces classify + branch.

**Cons:**
- Over-engineered for this codebase. Each handler is a closure capturing
  different context (mult_lookup, input_names, ctx, etc.). The 6-callback
  dataclass becomes boilerplate at every call site.
- Recursive sites (`_walk_aggregation_ast`, `reconstruct_expression`) need
  to reference themselves inside their own handlers (closures work but are
  awkward).
- `_unwrap_invocation` doesn't use 3 of the 6 handlers. Would need
  `on_operator=lambda n: n` passthrough stubs.
- The `Generic[T]` parameter doesn't buy much — the handlers already define
  the return type implicitly.

#### Recommendation: Option A

The classify function is the right abstraction level for this codebase. The
7 dispatch sites have nothing in common besides "identify the node type."
Forcing them into a callback framework would add complexity without reducing
the bug surface (the ordering bug is already eliminated by `classify_ast_node()`).

Option B could be built on top of Option A later if the codebase grows
enough call sites to justify it — `classify_ast_node()` is the foundation
for both.

---

### Workstream 2: Resolution Route Cleanup

#### Option A: Shared Utility Functions

Extract 1-2 focused utility functions for the common registry resolution
pattern. Keep the CalcUsage and aggregation resolution paths as separate
top-level functions.

```python
# core/resolution_utils.py

def resolve_scoped(
    output_registry: OutputRegistry,
    ref: str,
    scope_prefix: str | None = None,
) -> str | None:
    """Try scoped then unscoped registry resolution.

    1. If scope_prefix: resolve(f"{scope_prefix}.{ref}")
    2. Always:          resolve(ref)

    Returns canonical channel name or None.
    """
    if scope_prefix:
        channel = output_registry.resolve(f"{scope_prefix}.{ref}")
        if channel is not None:
            return channel
    return output_registry.resolve(ref)
```

The backtracker's `_resolve_reference_via_registry()` and the graph builder's
registry fallback section (lines 815-847) both become calls to
`resolve_scoped()` with their own scope prefix construction.

**Pros:**
- Minimal change. The two resolution paths retain their own top-level
  functions and domain-specific logic.
- Eliminates the specific duplication (key construction + fallback cascade)
  without coupling the two paths.
- Easy to test — the utility function has no domain-specific dependencies.

**Cons:**
- The shared operation is narrow (really just "try with prefix, then without").
  The utility function may feel trivial. But trivial is fine — the point is
  one place for the pattern, not code golf.

#### Option B: Unified Resolver Class

```python
class ChannelResolver:
    """Unified resolution for all input types."""
    def __init__(self, output_registry, redefinitions, design_attrs, ...): ...

    def resolve_binding(self, binding, usage) -> BindingResolution: ...
    def resolve_aggregation_term(self, term, instance_path) -> str | None: ...
    def resolve_local_term(self, term, instance_path) -> str | None: ...
```

**Pros:**
- Single place to understand ALL resolution logic.
- Could enforce consistent fallback behavior.

**Cons:**
- The two paths have genuinely different semantics, different return types
  (`BindingResolution` vs `str | None`), and different domain-specific
  strategies (CHAIN recursive, REFERENCE secondary, design attribute lookup).
  Forcing them into one class creates a god-object with method-level
  branching that reconstructs the original bifurcation inside one file.
- The backtracker owns its resolution as a method on `DependencyBacktracker`.
  Moving it to a separate class would require either (a) the backtracker
  delegating to the resolver, or (b) the resolver knowing about
  `DependencyBacktracker` internals. Both create coupling.
- The aggregation resolution has CHAIN recursive resolution with cycle
  detection — this is tied to the redefinition hierarchy and doesn't belong
  in a general-purpose resolver.

#### Recommendation: Option A

The actual duplication is narrow. Shared utility functions address it without
introducing coupling between paths that solve fundamentally different problems.
Option B would create more complexity than it removes.

---

## Proposed Design

### Component 1: AST Node Classifier

**File:** `src/sysml_codegen/extraction/ast_dispatch.py` (NEW)

**Location rationale:** In `extraction/` because all 7 consumers are in the
extraction or analysis layers. Not in `core/` because it depends on
`SysideAdapter` (an extraction-layer dependency) and `expression_utils`
(extraction-layer helper).

**Contents:**

1. `ASTNodeKind` enum — 6 values: FEATURE_CHAIN, FEATURE_REFERENCE, OPERATOR,
   INVOCATION, LITERAL, UNKNOWN

2. `classify_ast_node(node: Any) -> ASTNodeKind` — the single dispatch point.
   Enforces: FCE before FRE before OE before hasattr(function) before literal
   before unknown.

3. `classify_ast_node_with_details(node: Any) -> tuple[ASTNodeKind, dict[str, Any]]`
   — optional richer variant that also extracts commonly-needed attributes
   (operator, operands, function_name, referent_name, chain_name, literal_value)
   in one pass. This avoids the pattern where consumers classify and then
   immediately re-inspect the same attributes. **Only add this if migration
   reveals multiple sites doing classify-then-extract.**

**Dependencies:** `SysideAdapter`, `is_literal_expression` (from expression_utils)

### Component 2: Migration of 7 Dispatch Sites

Each site replaces its `is_instance()` chain with a call to
`classify_ast_node()`. The type-specific handler code within each site is
unchanged — only the branching structure changes.

**Site 1: `_extract_single_redefinition()`** (hierarchy_resolver.py:94-136)

Currently correct but independent. Migration:
```python
# Before:
if is_literal_expression(expr): ...
if SysideAdapter.is_instance(expr, "FeatureChainExpression"): ...
if SysideAdapter.is_instance(expr, "FeatureReferenceExpression"): ...
# fallback: EXPRESSION

# After:
kind = classify_ast_node(expr)
if kind == ASTNodeKind.LITERAL: ...
elif kind == ASTNodeKind.FEATURE_CHAIN: ...
elif kind == ASTNodeKind.FEATURE_REFERENCE: ...
else: ...  # EXPRESSION (covers OPERATOR, INVOCATION, UNKNOWN)
```

The EXPRESSION fallback covers OE, Invocation, and Unknown — matching current
behavior where anything that's not literal/FCE/FRE becomes EXPRESSION.

**Site 2: `_unwrap_invocation()`** (hierarchy_resolver.py:278-302)

Special case — only checks 3 types. Migration:
```python
kind = classify_ast_node(node)
if kind in (ASTNodeKind.FEATURE_CHAIN, ASTNodeKind.FEATURE_REFERENCE):
    return node  # terminal
if kind == ASTNodeKind.INVOCATION:
    operands = list(getattr(node, "operands", []))
    if operands:
        return _unwrap_invocation(operands[0], _depth + 1)
return node  # everything else: return as-is
```

Note: The current code checks `hasattr(node, "function")` which would match
FCE and FRE too (they have `function` attribute). But the FCE/FRE checks
come first, so they never reach the `hasattr` check. After migration this is
explicit — FCE/FRE are terminal, INVOCATION unwraps, everything else returns.

**Site 3: `_walk_aggregation_ast()`** (hierarchy_resolver.py:305-433)

The primary motivation for this work. After Bug A fix, FCE is already before
OE. Migration makes it canonical:
```python
kind = classify_ast_node(node)
if kind == ASTNodeKind.OPERATOR:
    # existing OE handler unchanged (recurse operands)
elif kind == ASTNodeKind.FEATURE_CHAIN:
    # existing SingletonTerm handler unchanged
elif kind == ASTNodeKind.FEATURE_REFERENCE:
    # existing LocalTerm handler unchanged
elif kind == ASTNodeKind.INVOCATION:
    # existing sum/wrapper handler unchanged
elif kind == ASTNodeKind.LITERAL:
    return reconstruct_expression(node)
else:  # UNKNOWN
    ctx.has_unsupported = True
    logger.warning(...)
```

**Site 4: `reconstruct_expression()`** (expression_utils.py:34-76)

Currently wrong in committed code (OE before FCE); fixed in working tree
by the Bug A changes. Migration replaces the ad-hoc fix with canonical
dispatch:
```python
kind = classify_ast_node(expr_node)
if kind == ASTNodeKind.OPERATOR:
    return reconstruct_operator_expression(expr_node)
elif kind == ASTNodeKind.FEATURE_REFERENCE:
    return extract_feature_reference_name(expr_node)
elif kind == ASTNodeKind.FEATURE_CHAIN:
    return extract_feature_chain_name(expr_node)
elif kind == ASTNodeKind.INVOCATION:
    func_name = expr_node.function.name
    ...
elif kind == ASTNodeKind.LITERAL:
    # existing literal handling (LiteralInteger, etc.)
else:  # UNKNOWN
    return str(expr_node)
```

**Circular dependency note:** `reconstruct_expression` in `expression_utils`
will import `classify_ast_node` from `ast_dispatch`. If `ast_dispatch` also
imported `is_literal_expression` from `expression_utils`, that would be a
circular import. **Resolution:** `ast_dispatch.py` includes its own private
`_is_literal()` (shown in the classify_ast_node code above) that performs
the same `is_instance` checks plus `NullExpression`. No import from
`expression_utils` is needed. `expression_utils.is_literal_expression`
remains available for other consumers but is not used by `ast_dispatch`.

**Site 5: `build_expression_ast()`** (expression_compiler.py:290-405)

Currently wrong (OE before FCE). After Bug A bugfix fixes this, migration
makes it canonical:
```python
kind = classify_ast_node(syside_node)
if kind == ASTNodeKind.OPERATOR:
    # existing OE handler (unit annotation, binary, unary, n-ary)
elif kind == ASTNodeKind.FEATURE_REFERENCE:
    # existing FRE handler (input_ref, intermediate_ref, unsupported)
elif kind == ASTNodeKind.LITERAL:
    # existing literal handler
elif kind == ASTNodeKind.FEATURE_CHAIN:
    return ExpressionAST.unsupported(...)
else:  # INVOCATION, UNKNOWN
    return ExpressionAST.unsupported(...)
```

**Site 6: `_extract_single_binding()`** (usage_extractor.py:503-571)

Currently correct. Migration:
```python
kind = classify_ast_node(expr)
if kind == ASTNodeKind.FEATURE_CHAIN:
    # existing CHAIN handler
elif kind == ASTNodeKind.FEATURE_REFERENCE:
    # existing REFERENCE handler
elif kind == ASTNodeKind.LITERAL:
    # existing LITERAL handler
elif kind == ASTNodeKind.OPERATOR:
    # existing EXPRESSION handler
else:  # INVOCATION, UNKNOWN
    return BindingInfo(..., binding_type=BindingType.UNBOUND, ...)
```

**Site 7: `_extract_default_value()`** (parameter_groups.py:158-199)

Currently correct. Migration:
```python
kind = classify_ast_node(expr)
if kind == ASTNodeKind.LITERAL:
    # existing per-literal-type handling (int, rational, bool, string)
    # NOTE: still needs sub-classification within LITERAL — see below
elif kind == ASTNodeKind.FEATURE_REFERENCE:
    return _extract_reference_path(expr)
elif kind == ASTNodeKind.FEATURE_CHAIN:
    return _extract_chain_path(expr)
elif kind == ASTNodeKind.OPERATOR:
    return str(evaluate_true_static_expression(expr))
else:
    return str(expr) if hasattr(expr, "__str__") else None
```

**Sub-classification within LITERAL:** Sites 4, 5, and 7 need to distinguish
literal sub-types (LiteralInteger vs LiteralReal vs LiteralBoolean vs
LiteralString vs LiteralRational vs NullExpression). `classify_ast_node()`
returns `LITERAL` for all of these. Sites that need sub-type info can use
`type(node).__name__` directly — this is safe because the `LITERAL` branch
is only reached for actual literal nodes. No additional enum values needed.

**LITERAL branch fallback rule:** Each site's LITERAL handler MUST include
an internal fallback for unhandled sub-types. Before migration, unhandled
literal sub-types (e.g., LiteralReal in `_extract_default_value()`) fall
through the entire `if/elif` chain to the function's final fallback.
After migration, they enter the LITERAL branch and could silently produce
no return value. Each LITERAL branch must end with an `else` that
preserves the site's original fallback behavior (e.g.,
`return str(expr) if hasattr(expr, "__str__") else None` for Site 7).

### Component 3: Shared Resolution Utility

**File:** `src/sysml_codegen/core/resolution_utils.py` (NEW)

**Location rationale:** In `core/` because it depends only on `OutputRegistry`
(which is in `core/`). Both consumers (backtracker in `analysis/`,
graph_builder in `resolution/`) import from `core/`.

**Contents:**

```python
def resolve_scoped(
    output_registry: OutputRegistry,
    ref: str,
    scope_prefix: str | None = None,
) -> str | None:
    """Try scoped then unscoped registry resolution.

    Resolution order:
    1. If scope_prefix provided: resolve("{scope_prefix}.{ref}")
    2. Always: resolve(ref) directly

    Returns canonical channel name or None.
    """
    if scope_prefix:
        scoped_key = f"{scope_prefix}.{ref}"
        channel = output_registry.resolve(scoped_key)
        if channel is not None:
            return channel
    return output_registry.resolve(ref)
```

### Component 4: Migration of Resolution Paths

**Aggregation path** (`graph_builder.py:815-847`):

The registry fallback section of `_resolve_aggregation_input_channel()` becomes:

```python
# Before (lines 815-847):
instance_parts = instance_path.split("__")
if len(instance_parts) > 1:
    dotted_scope = ".".join(instance_parts[1:])
    scoped_key = f"{dotted_scope}.{part_usage}.{attr}"
    channel = output_registry.resolve(scoped_key)
    if channel is not None:
        return channel
catalog_key = f"{part_usage}.{attr}"
channel = output_registry.resolve(catalog_key)
if channel is not None:
    return channel
return None

# After:
instance_parts = instance_path.split("__")
scope_prefix = ".".join(instance_parts[1:]) if len(instance_parts) > 1 else None
ref = f"{part_usage}.{attr}"
return resolve_scoped(output_registry, ref, scope_prefix)
```

**CalcUsage path** (`dependency_backtracker.py:440-453`):

The REFERENCE secondary resolution's scoped lookup becomes:

```python
# Before:
parent_part = self._get_parent_part_for_usage(usage)
if parent_part:
    scoped_key = f"{parent_part}.{leaf}"
    channel = self._output_registry.resolve(scoped_key)
    if channel is not None:
        ...

# After:
parent_part = self._get_parent_part_for_usage(usage)
channel = resolve_scoped(self._output_registry, leaf, parent_part)
if channel is not None:
    ...
```

**Bug B's LocalTerm resolution** (graph_builder.py:1015-1036, added by bugfix):

The new sibling agg output lookup would also use `resolve_scoped()`:

```python
# In _build_aggregation_module LocalTerm processing:
instance_parts = agg.instance_path.split("__")
part_usage = instance_parts[-1]
ref = f"{part_usage}.{l_term.attribute_name}"
scope_prefix = ".".join(instance_parts[1:]) if len(instance_parts) > 1 else None
channel = resolve_scoped(output_registry, ref, scope_prefix)
```

**What stays domain-specific (NOT migrated):**

- CHAIN recursive resolution in `_resolve_aggregation_input_channel()` (lines
  789-813) — hierarchy-specific, with cycle detection
- REFERENCE secondary resolution in backtracker (lines 422-453) — SYSML_QN
  leaf extraction is specific to REFERENCE bindings
- Design attribute fallback in backtracker (lines 530-609) — design attribute
  lookup is specific to CalcUsage binding resolution
- Self-reference guard in backtracker (lines 488-494) — only CalcUsage
  bindings have self-reference semantics
- Canonical channel verification in graph_builder — stays in the aggregation
  path (the direct channel construction fallback at lines 972-984 still needs it)

**FR-5 deviation note:** The spec (FR-5) lists "canonical channel verification"
as minimum shared scope. However, research shows this operation is aggregation-
only — the CalcUsage path trusts registry results directly (None = not found)
and never verifies against a canonical channels set. Extracting a single-
consumer operation into shared infrastructure would add indirection without
reducing duplication. **Recommendation:** amend spec FR-5 to remove "canonical
channel verification" from the minimum shared scope.

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Circular import between ast_dispatch and expression_utils | Build failure | `ast_dispatch.py` includes its own `_is_literal()` (with NullExpression) — no import from expression_utils |
| LITERAL branch swallows unhandled sub-types | Silent None return | Each site's LITERAL handler must include an internal `else` fallback preserving original behavior |
| Migration changes behavior subtly | Wrong wiring | All existing tests must pass. Spike script re-run validates aggregation wiring counts. |
| `_unwrap_invocation` doesn't fit the pattern | Forced abstraction | It works fine with classify — just uses 3 of 6 enum values. |
| `resolve_scoped` is too simple to justify | Over-engineering perception | It's 8 lines. The value is one place for the pattern + explicit naming. If it feels too thin, it could live as a method on OutputRegistry instead. |
| Future node types not in the enum | Classification gap | UNKNOWN catches all unrecognized types with a log warning. New types can be added to the enum and classifier when encountered. |

---

## Integration Strategy

**Ordering:** Workstream 1 (AST dispatcher) first, Workstream 2 (resolution
utilities) second. They are independent, but the AST dispatcher is the higher
priority (prevents a bug class) while the resolution utility is pure cleanup.

**Migration strategy:** One site at a time, test after each. The enum +
classify function is additive — it doesn't break anything until a site is
migrated. Sites can be migrated in any order.

**Suggested migration order:**
1. Create `ast_dispatch.py` with `ASTNodeKind` + `classify_ast_node()`
2. Migrate `reconstruct_expression()` (the one remaining wrong-ordering site)
3. Migrate `_walk_aggregation_ast()` (the primary motivation, already fixed by Bug A)
4. Migrate `build_expression_ast()` (already fixed by Bug A)
5. Migrate remaining 4 correct sites
6. Create `resolution_utils.py` with `resolve_scoped()`
7. Migrate aggregation registry fallback
8. Migrate backtracker REFERENCE secondary

---

## Validation Approach

**Unit tests for `ast_dispatch.py`:**
- Test `classify_ast_node()` with mock nodes matching each of the 6 kinds
- Test that FCE node returns FEATURE_CHAIN (not OPERATOR) — the key property
- Test that FRE node returns FEATURE_REFERENCE (not INVOCATION)
- Test that None returns UNKNOWN
- Test that unrecognized node returns UNKNOWN

**Unit tests for `resolve_scoped()`:**
- Test scoped hit (prefix + ref resolves)
- Test scoped miss, unscoped hit (prefix + ref fails, ref alone resolves)
- Test both miss (returns None)
- Test no prefix (goes straight to unscoped)

**Integration validation:**
- All 647+ existing tests pass
- Re-run spike script (`scripts/spike_agg_wiring_h1_h4.py`) — identical
  results confirm no behavioral change in aggregation wiring
- Grep for remaining `is_instance.*FeatureChainExpression` and
  `is_instance.*OperatorExpression` calls — should only exist in
  `classify_ast_node()` and `_is_literal()` (and the SysideAdapter itself)

---

**Next Steps:** After approval → `/_my_plan` for implementation phasing.
