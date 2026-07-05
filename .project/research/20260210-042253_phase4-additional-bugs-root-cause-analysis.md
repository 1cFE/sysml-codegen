---
date: 2026-02-10T04:22:53+00:00
researcher: Claude
topic: "Root cause analysis of 3 additional codegen bugs found during Phase 4 E2E validation"
tags: [research, codegen, bugs, smart-regen, sanitization, package-init]
status: complete
last_updated: 2026-02-10
---

# Research: Phase 4 Additional Bugs Root Cause Analysis

**Date**: 2026-02-10T04:22:53+00:00
**Researcher**: Claude
**Research Type**: Codebase / Bug Analysis

## Research Question

During Phase 4 (Solar Battery Regeneration + Merge) of E2E attribute expression validation, 3 additional codegen bugs were discovered beyond the 4 found in Phase 3. What are the root causes, and what are the correct fixes?

The bugs (from fusion-tea plan.md, Phase 4 Completion notes):
5. **`--smart-regen` prevents auto-impl of unchanged-signature stubs** -- All 15 CalcDef stencils preserved because signatures matched, even though 10 are stubs with `raise NotImplementedError`. Auto-impl exists in compilation cache but isn't written.
6. **`&` in part names produces invalid Python identifiers** -- `Racking_&_Mounting` in SysML becomes `Racking_&_Mounting` in Python schema field names, causing SyntaxError.
7. **Missing `__init__.py` for computed attribute package directories** -- Codegen creates `modules/solarbatterydesign/solar_battery_plant/` with `__init__.py` but doesn't create `modules/solarbatterydesign/__init__.py`.

## Summary

- **Bug 5 is a design gap in smart-regen's preservation logic**: The `should_regenerate_stencil()` function compares only function signatures (name, input type, return type), which are identical between stubs and auto-implementations. The `else` (preserve) branch at `cli/__init__.py:459-461` has access to `compilation_result` but ignores it, unconditionally preserving stubs that could be upgraded to auto-implementations.
- **Bug 6 is an incomplete `sanitize_name()` function**: The canonical `sanitize_name()` in `core/qualified_names.py:12-27` handles quotes, spaces, and Python reserved words but has **no handling for special characters** (`&`, `$`, `@`, etc.). Any SysML name containing non-alphanumeric, non-underscore characters passes through verbatim into Python identifiers.
- **Bug 7 is a missing intermediate `__init__.py` creation**: All four namespace-creating functions (`_generate_modules`, `_generate_computed_attr_modules`, `_generate_stencils`, `_generate_computed_attr_stencils`) only write `__init__.py` to the deepest directory in `python_path.directory`. When computed attributes produce 2-level deep paths (e.g., `solarbatterydesign/solar_battery_plant/`), `mkdir(parents=True)` creates intermediate directories but no `__init__.py` is written there. CalcUsage modules are unaffected only because they have single-level paths.
- **All 3 bugs are fixable with well-scoped changes.** Bug 5 requires a 4-line check in the smart-regen preserve branch. Bug 6 requires adding a regex replacement in `sanitize_name()`. Bug 7 requires a helper function to ensure all directories in a path have `__init__.py`.

## Detailed Findings

### Bug 5: `--smart-regen` Prevents Auto-Impl of Unchanged-Signature Stubs

**Symptom**: Running `--smart-regen` on solar_battery preserves all 15 CalcDef `_impl.py` stencils unchanged, even though 10 are stubs containing `raise NotImplementedError` and auto-implementation code exists in the compilation results.

**Manual workaround applied**: None practical. The only workaround is to run without `--smart-regen`, which would overwrite the 5 genuinely hand-implemented files.

#### Root Cause: Signature comparison is body-agnostic; preserve branch ignores compilation state

The decision chain for `--smart-regen` is:

```
_generate_stencils()  (cli/__init__.py:398-482)
  ├── Lookup: compilation_result = ctx.compilation_results.get(calc_def.name)  [line 444]
  ├── IF smart_regen AND file exists:  [line 447]
  │   ├── should_regenerate_stencil(calc_def, output_path)  [line 448]
  │   │   ├── Extract existing signature from AST  [preservation.py:49]
  │   │   ├── Generate expected signature from calc_def  [preservation.py:55]
  │   │   └── Compare: name + input_type + return_type  [preservation.py:58]
  │   │
  │   ├── IF should_regen == True:  [line 449]
  │   │   └── generate_implementation(..., compilation_result=compilation_result)
  │   │       └── Dispatches to auto_implementation.py.jinja2 if FULLY_COMPILABLE
  │   │
  │   └── ELSE (should_regen == False):  [line 459]
  │       └── stats["preserved"] += 1   ← BUG: compilation_result NEVER checked
  │       └── (file preserved as-is, even if it's a stub)
```

**Why stubs and auto-impls have identical signatures:**

The `FunctionSignature.matches()` method (`analysis/signature_extractor.py:35-62`) compares:
- `function_name` (identical: both use `run_{calc_name}`)
- `input_type` (identical: both use same Input class)
- `return_type` (identical: both use same output type)

The function body (stub with `raise NotImplementedError` vs auto-impl with computed expressions) is **never compared**. This is correct by design -- the smart-regen feature's purpose is to detect interface changes, not body changes. But the preserve branch should still check whether a stub could be upgraded.

**Chain of failure:**
1. `compilation_result` is retrieved at line 444 and is `FULLY_COMPILABLE` for 10 CalcDefs
2. `should_regenerate_stencil()` returns `(False, "Signature unchanged")` because signatures match
3. The preserve branch at lines 459-461 preserves the file unconditionally
4. The `compilation_result` is never consulted in the preserve branch
5. Auto-impl code is never written

#### Clean Fix

**Add an "auto-impl upgrade" check in the preserve branch.**

After the `should_regen == False` decision (cli/__init__.py:459), check whether the existing file is a stub (no `AUTO_IMPLEMENTED = True` sentinel) AND an auto-impl is available (`compilation_result.overall_compilability == FULLY_COMPILABLE`). If both conditions are met, upgrade the stub to auto-impl (with backup):

```python
else:
    # Check if stub can be upgraded to auto-impl
    existing_content = output_path.read_text()
    is_stub = "AUTO_IMPLEMENTED = True" not in existing_content
    has_auto_impl = (
        compilation_result is not None
        and compilation_result.overall_compilability == Compilability.FULLY_COMPILABLE
    )
    if is_stub and has_auto_impl:
        backup_implementation(output_path, backup_dir)
        code = generate_implementation(
            calc_def, template_env, output_path, config.package_name,
            compilation_result=compilation_result,
        )
        if code:
            output_path.write_text(code)
        stats["regenerated"] += 1
        logger.debug(f"Upgraded stub to auto-impl: {output_path.name}")
    else:
        stats["preserved"] += 1
        logger.debug(f"Preserved stencil ({reason}): {output_path.name}")
```

**Why this is safe:**
- Files with `AUTO_IMPLEMENTED = True` are always preserved (machine-generated, no human edits)
- Files WITHOUT the sentinel are stubs OR hand-written implementations
- Hand-written implementations have custom function bodies, which means they almost certainly DON'T have `compilation_result.overall_compilability == FULLY_COMPILABLE` -- wait, that's wrong. `compilation_result` is per-CalcDef, not per-file. All CalcDefs with expression ASTs get compilation attempted regardless of file state.

**Revised approach:** Check for `raise NotImplementedError` in the existing file body, which is the definitive stub marker:

```python
is_stub = "raise NotImplementedError" in existing_content
```

This is more reliable because:
- Stubs always contain `raise NotImplementedError` (generated by `implementation_stencil.py.jinja2`)
- Hand-written implementations never contain it (the whole point is replacing it)
- Auto-implementations never contain it

**Files to change:**
- `src/sysml_codegen/cli/__init__.py` -- Lines 459-461: Add auto-impl upgrade check in preserve branch

---

### Bug 6: `&` in Part Names Produces Invalid Python Identifiers

**Symptom**: `Racking_&_Mounting` in the solar_battery SysML model produces `Racking_&_Mounting` in Python schema field names, causing `SyntaxError` when the generated schema module is imported.

**Manual workaround applied**: Removed `LibraryParams`/`DesignParams` imports from `__init__.py` to avoid triggering the SyntaxError.

#### Root Cause: Incomplete `sanitize_name()` function

The canonical name sanitization lives in `core/qualified_names.py:12-27`:

```python
def sanitize_name(name: str | None) -> str:
    if not name:
        return ""
    name = name.strip("'\"")        # Handles quotes
    name = name.replace(" ", "_")    # Handles spaces
    if name in {"class", "def", "import", "from", "return", "yield"}:
        name = f"{name}_"            # Handles reserved words
    return name
```

**Missing: Any handling of non-alphanumeric, non-underscore characters.** The character `&` in `Racking_&_Mounting` passes through unchanged.

There is also a **duplicate** `_sanitize_name()` method in `extraction/extractor.py:616-624` with identical logic, same missing handling.

**Impact path:**

```
SysML: "Racking_&_Mounting" (part name in solar_battery design)
  ↓
sanitize_name("Racking_&_Mounting") → "Racking_&_Mounting"  [NO CHANGE]
  ↓
build_element_qualified_name() → "...Racking_&_Mounting"
  ↓
EntryPoint.simple_name / qualified_name contain "&"
  ↓
Schema generation (entry_point.py:103-187) uses name directly
  ↓
Template (parameter_group_schema.py.jinja2) renders {{ field.name }}
  ↓
Generated Python: `Racking_&_Mounting: float = Field(...)`
  ↓
SyntaxError: `&` is not valid in a Python identifier
```

**Where names enter the pipeline:**
- `extraction/extractor.py:93` -- Part definition extraction calls `sanitize_name()`
- `extraction/extractor.py:132` -- CalcDef extraction
- `extraction/extractor.py:341` -- Attribute name extraction
- `analysis/parameter_groups.py:132` -- Design attribute parameter derivation

**Where names are rendered into Python code:**
- `generation/entry_point.py:103-187` -- `generate_entry_point_schema()` uses `attr.name` as schema field
- `generation/entry_point.py:387-443` -- `generate_derived_group_schema()` uses `param.name`
- `templates/parameter_group_schema.py.jinja2` -- `{{ field.name }}` rendered directly
- `templates/entry_point_schema.py.jinja2` -- `{{ field.name }}` rendered directly
- `templates/multioutput_model.py.jinja2` -- `{{ field.name }}` rendered directly

#### Clean Fix

**Extend `sanitize_name()` to strip all non-identifier characters.**

In `core/qualified_names.py:12-27`:

```python
import re

def sanitize_name(name: str | None) -> str:
    """Sanitize SysML name for Python.

    Args:
        name: Raw SysML name (may contain quotes, spaces, special chars)

    Returns:
        Python-safe identifier string
    """
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    # Replace any non-alphanumeric, non-underscore characters with underscore
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Collapse multiple underscores
    name = re.sub(r"__+", "_", name)
    # Strip leading/trailing underscores (but preserve at least the name)
    name = name.strip("_") or name
    if name in {"class", "def", "import", "from", "return", "yield"}:
        name = f"{name}_"
    return name
```

**Result**: `Racking_&_Mounting` → `Racking_Mounting` (valid Python identifier).

**Note on underscore collapsing**: The regex `__+` collapsing is important because `__` is the ADR-003 hierarchy separator. If a sanitized name produced `foo__bar`, it could be confused with a qualified name separator. A single `_` is the right replacement. However, this collapsing should ONLY happen within `sanitize_name()` (individual name segments), not in the qualified name builder where `__` is intentional.

**Also fix the duplicate:** Remove `extraction/extractor.py:616-624` (`_sanitize_name()` method) and replace calls to it with `from sysml_codegen.core.qualified_names import sanitize_name`. This eliminates the code duplication that would otherwise require fixing the same bug in two places.

**Files to change:**
- `src/sysml_codegen/core/qualified_names.py` -- Lines 12-27: Add `re.sub` for non-identifier characters
- `src/sysml_codegen/extraction/extractor.py` -- Lines 616-624: Remove duplicate, use canonical import

---

### Bug 7: Missing `__init__.py` for Intermediate Package Directories

**Symptom**: Codegen creates `modules/solarbatterydesign/solar_battery_plant/` with its own `__init__.py` but doesn't create `modules/solarbatterydesign/__init__.py`. Python import of `modules.solarbatterydesign.solar_battery_plant.p_net_kw` fails because the intermediate directory isn't a valid Python package.

**Manual workaround applied**: Manually created 2 missing `__init__.py` files (`modules/solarbatterydesign/__init__.py` and `handwritten/solarbatterydesign/__init__.py`).

#### Root Cause: All four namespace-creating functions only write `__init__.py` to the deepest directory

All four module/stencil generation functions share the same pattern for namespace directory creation:

```python
if python_path.directory:
    namespace_dir = base_dir / python_path.directory
    namespace_dir.mkdir(parents=True, exist_ok=True)    # Creates ALL dirs
    init_file = namespace_dir / "__init__.py"             # Only deepest dir
    if not init_file.exists():
        init_file.write_text('"""..."""\n')
```

`mkdir(parents=True)` creates the full directory tree (e.g., both `solarbatterydesign/` and `solarbatterydesign/solar_battery_plant/`), but the `__init__.py` is only written to `namespace_dir` (the deepest directory in the path). Intermediate directories are left without `__init__.py`.

**Why CalcUsage modules are unaffected:**

CalcDef qualified names have the structure `Package::CalcDef` (2 segments). This produces:
- `package_segments` = `["Package"]` → 1 level
- `directory` = `"package"` → single directory, no intermediates needed

Computed attribute qualified names have `Design::PartUsage::AttrName` (3 segments):
- `package_segments` = `["Design", "PartUsage"]` → 2 levels
- `directory` = `"design/partusage"` → nested directory, intermediate needed

**Proof:** For `SolarBatteryDesign::solar_battery_plant::p_net_kw`:
- `directory` = `"solarbatterydesign/solar_battery_plant"`
- `namespace_dir` = `modules/solarbatterydesign/solar_battery_plant/`
- `__init__.py` written to: `modules/solarbatterydesign/solar_battery_plant/__init__.py` (correct)
- `__init__.py` NOT written to: `modules/solarbatterydesign/__init__.py` (BUG)

**Affected functions (all four):**

| Function | File:Lines | Creates `__init__.py` for intermediates? |
|----------|-----------|----------------------------------------|
| `_generate_modules` | `cli/__init__.py:180-189` | No (latent bug, never triggered) |
| `_generate_computed_attr_modules` | `cli/__init__.py:239-244` | No (**active bug**) |
| `_generate_stencils` | `cli/__init__.py:430-437` | No (latent bug, never triggered) |
| `_generate_computed_attr_stencils` | `cli/__init__.py:347-352` | No (**active bug**) |

Note: `_generate_modules` and `_generate_stencils` have a `created_namespaces` set for deduplication, but this only prevents writing `__init__.py` multiple times to the *same* deepest directory -- it doesn't address intermediate directories. The `created_namespaces` set provides optimization, not correctness.

#### Clean Fix

**Create a helper function that ensures all directories in a path have `__init__.py`.**

```python
def _ensure_package_init_files(base_dir: Path, relative_path: str, docstring: str = '"""Namespace package."""\n') -> None:
    """Ensure __init__.py exists in all directories along relative_path under base_dir."""
    parts = relative_path.split("/")
    current = base_dir
    for part in parts:
        current = current / part
        init_file = current / "__init__.py"
        if not init_file.exists():
            init_file.write_text(docstring)
```

Then replace all four namespace creation patterns with:

```python
if python_path.directory:
    namespace_dir = base_dir / python_path.directory
    namespace_dir.mkdir(parents=True, exist_ok=True)
    _ensure_package_init_files(base_dir, python_path.directory, docstring)
```

**Files to change:**
- `src/sysml_codegen/cli/__init__.py` -- Add `_ensure_package_init_files()` helper
- `src/sysml_codegen/cli/__init__.py` -- Lines 180-189: Update `_generate_modules` to use helper
- `src/sysml_codegen/cli/__init__.py` -- Lines 239-244: Update `_generate_computed_attr_modules` to use helper
- `src/sysml_codegen/cli/__init__.py` -- Lines 347-352: Update `_generate_computed_attr_stencils` to use helper
- `src/sysml_codegen/cli/__init__.py` -- Lines 430-437: Update `_generate_stencils` to use helper

---

## Cross-Bug Analysis

### Relationship Between Bugs 5-7

These three bugs are independent with no shared root cause. Each affects a different phase of code generation:

| Bug | Generation Phase | Root Issue |
|-----|-----------------|------------|
| #5 | Stencil writing (output phase) | Smart-regen logic gap |
| #6 | Name extraction (input phase) | Incomplete sanitization |
| #7 | Directory setup (infrastructure) | Missing intermediate `__init__.py` |

### Priority Order for Fixes

| Priority | Bug | Effort | Impact | Risk |
|----------|-----|--------|--------|------|
| 1 | Bug 6 (`&` sanitization) | Trivial | Prevents SyntaxError in any model with special chars | Low -- regex is well-understood |
| 2 | Bug 7 (missing `__init__.py`) | Low | Prevents ImportError for all computed attr models with nested paths | Low -- helper function is simple |
| 3 | Bug 5 (smart-regen stub upgrade) | Low-Medium | Enables auto-impl for all unchanged-signature CalcDefs | Medium -- needs careful sentinel checking |

Bug 6 should be fixed first because it's the most broadly impactful (any SysML model with special characters in names) and most likely to cause confusion (SyntaxError in generated code with no obvious cause).

### Latent Bugs Identified

1. **Bug 7 is latent in `_generate_modules` and `_generate_stencils`**: These functions have the same `__init__.py` creation pattern as the computed attr functions, but are never triggered because CalcUsage qualified names produce single-level paths. When Phase 3 introduces CalcUsages-in-PartDefs (nested hierarchies), these will have multi-level paths and the same bug will manifest.

2. **Bug 6 affects ALL name paths in the pipeline**: The `sanitize_name()` function is used in qualified name building, parameter grouping, and schema generation. Any SysML model element with special characters in its name will produce invalid Python identifiers. The solar_battery's `Racking_&_Mounting` is the first instance encountered, but others may exist in other models.

## Code References

### Bug 5 (Smart-Regen Stub Upgrade)
- `src/sysml_codegen/cli/__init__.py:444` -- `compilation_result` lookup (available but unused in preserve branch)
- `src/sysml_codegen/cli/__init__.py:447-461` -- Smart-regen decision: lines 459-461 are the BUG (unconditional preserve)
- `src/sysml_codegen/generation/preservation.py:20-61` -- `should_regenerate_stencil()` (signature-only comparison)
- `src/sysml_codegen/analysis/signature_extractor.py:35-62` -- `FunctionSignature.matches()` (compares name+types, not body)
- `src/sysml_codegen/generation/stencils.py:233-272` -- `generate_implementation()` (template dispatch based on compilation_result)
- `src/sysml_codegen/generation/stencils.py:255-268` -- Auto-impl vs stub template selection

### Bug 6 (`&` Sanitization)
- `src/sysml_codegen/core/qualified_names.py:12-27` -- `sanitize_name()` (MISSING special char handling)
- `src/sysml_codegen/extraction/extractor.py:616-624` -- Duplicate `_sanitize_name()` (same missing handling)
- `src/sysml_codegen/core/qualified_names.py:30-54` -- `build_element_qualified_name()` (calls sanitize_name)
- `src/sysml_codegen/core/qualified_names.py:67` -- `_build_owner_chain_with_packages()` (calls sanitize_name)
- `src/sysml_codegen/analysis/parameter_groups.py:132` -- Design attribute name derivation using sanitize_name
- `src/sysml_codegen/generation/entry_point.py:103-187` -- Schema generation uses unsanitized names
- `src/sysml_codegen/templates/parameter_group_schema.py.jinja2` -- `{{ field.name }}` rendered directly

### Bug 7 (Missing `__init__.py`)
- `src/sysml_codegen/cli/__init__.py:180-189` -- `_generate_modules` namespace creation (latent bug)
- `src/sysml_codegen/cli/__init__.py:239-244` -- `_generate_computed_attr_modules` namespace creation (**active bug**)
- `src/sysml_codegen/cli/__init__.py:347-352` -- `_generate_computed_attr_stencils` namespace creation (**active bug**)
- `src/sysml_codegen/cli/__init__.py:430-437` -- `_generate_stencils` namespace creation (latent bug)
- `src/sysml_codegen/core/identifier_types.py:74-78` -- `PythonModulePath.from_sysml()` (produces multi-level directory)
- `src/sysml_codegen/core/identifier_types.py:22-24` -- `SysMLQualifiedName.package_segments` (determines nesting depth)

## Recommendations

### Immediate Actions

1. **Fix Bug 6** (trivial, broad impact): Add `re.sub(r"[^a-zA-Z0-9_]", "_", name)` to `sanitize_name()` in `core/qualified_names.py:12-27`. Remove duplicate in `extraction/extractor.py:616-624`.
2. **Fix Bug 7** (low effort, prevents ImportError): Add `_ensure_package_init_files()` helper, update all 4 namespace creation patterns.
3. **Fix Bug 5** (low-medium effort, enables auto-impl): Add stub-detection check (`"raise NotImplementedError" in content`) in smart-regen preserve branch. Upgrade stubs to auto-impl when compilation_result is FULLY_COMPILABLE.

### Testing Strategy

After fixes:
1. **Bug 6**: Add unit test for `sanitize_name()` with inputs: `"Racking_&_Mounting"`, `"foo$bar"`, `"a@b"`, `"hello-world"`. Verify all produce valid Python identifiers.
2. **Bug 7**: Regenerate solar_battery and verify `modules/solarbatterydesign/__init__.py` exists. Add test that all directories in generated output contain `__init__.py`.
3. **Bug 5**: Regenerate solar_battery with `--smart-regen`. Verify 10 stubs are upgraded to auto-impl (check `AUTO_IMPLEMENTED = True` sentinel). Verify 5 hand-written implementations are preserved.

### Architectural Observation

Bug 5 reveals a fundamental tension in the smart-regen feature: **signature preservation is necessary for protecting hand-written code, but insufficient for distinguishing stubs from implementations.** The `AUTO_IMPLEMENTED = True` sentinel and the `raise NotImplementedError` pattern provide the additional signal needed to make the correct decision. The fix elegantly resolves this by adding body-awareness only where it matters (the preserve branch), keeping the signature comparison clean.

## Open Questions

1. **Should `sanitize_name()` handle Unicode identifiers?** Python 3 supports Unicode identifiers (PEP 3131). The current fix strips all non-ASCII characters. If SysML models use Unicode names (e.g., Greek letters for physics), these would be replaced with underscores. For now, ASCII-only is sufficient for the solar_battery and e2e_attr_expr models.

2. **Should the underscore collapsing in `sanitize_name()` preserve double underscores?** The `__` separator is used by ADR-003 for qualified names. If a raw SysML name like `foo & bar` sanitizes to `foo___bar` and then collapses to `foo_bar`, that's correct. But if `sanitize_name()` receives an already-qualified name, collapsing `__` would break it. The current usage pattern (sanitize individual name segments, then join with `__`) is correct, so collapsing within `sanitize_name()` is safe.

3. **What happens with existing generated files that have `&` in names?** The solar_battery model's `Racking_&_Mounting` currently produces broken Python files. After the fix, regenerating will produce different field names (`Racking_Mounting` instead of `Racking_&_Mounting`). Any hand-crafted code referencing the old (broken) names won't exist because the files were never importable. So this is a clean migration.
