# 23 -- Smart Regeneration and Implementation Preservation

## The Problem

When the SysML model changes and codegen re-runs, handwritten implementation
files (`handwritten/*_impl.py`) can be overwritten. Smart-regen compares
function signatures to preserve handwritten code when the interface hasn't
changed, and upgrades stubs to auto-implementations when possible.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-SR-01 | Signature comparison SHALL use two-level matching: type-level (required) then field-level (optional) | `matches()` at `signature_extractor.py:35-62` |
| REQ-SR-02 | Field comparison SHALL be order-independent (sorted) | `sorted(self.input_fields) == sorted(other.input_fields)` |
| REQ-SR-03 | `should_regenerate_stencil()` SHALL implement the [4-case decision tree](#the-4-case-decision-tree) | 4 return paths in `preservation.py:20-61` |
| REQ-SR-04 | Stub upgrade SHALL require all 3 conditions: signature match, `NotImplementedError` present, `FULLY_COMPILABLE` | `cli/__init__.py:659-691` checks all three |
| REQ-SR-05 | Backup SHALL be created before every regeneration or upgrade | `backup_implementation()` called before `write_text()` |
| REQ-SR-06 | Aggregation and [computed-attribute](16-computed-attributes.md) modules SHALL NOT use smart-regen (always regenerated) | No `smart_regen` references in `_generate_aggregation_stencils()` or `_generate_computed_attr_stencils()` |
| REQ-SR-07 | `--preserve-handwritten` SHALL skip ALL existing handwritten files without comparison | Blanket skip, no signature extraction |

---

## FunctionSignature Data Model

**File**: `analysis/signature_extractor.py:16-33`

```python
@dataclass
class FunctionSignature:
    function_name: str              # "run_alphaneutronsplit"
    input_type: str                 # "AlphaNeutronSplitInput"
    return_type: str                # "float" or "tuple[float, float]"
    input_fields: list[str] | None  # ["n_alpha_in", "n_neutron_in"] or None
```

### matches() Method (lines 35-62)

Two-level comparison:

```python
def matches(self, other: "FunctionSignature") -> bool:
    # Level 1: Type-level (REQUIRED)
    if not (self.function_name == other.function_name
            and self.input_type == other.input_type
            and self.return_type == other.return_type):
        return False
    # Level 2: Field-level (OPTIONAL -- only if both have fields)
    if self.input_fields is not None and other.input_fields is not None:
        return sorted(self.input_fields) == sorted(other.input_fields)
    return True  # Graceful fallback if either side has None
```

Field comparison is **order-independent** (sorted). If either signature
has `input_fields=None` (legacy files or unmodified stubs), field
comparison is skipped and only type-level checks apply.

---

## Signature Extraction

### From Existing File (lines 148-192)

`extract_signature_from_impl(impl_path: Path) -> FunctionSignature | None`

Uses Python AST to find `run_*` function:
1. Parse source with `ast.parse()`
2. Walk AST for `FunctionDef` nodes starting with `run_`
3. Extract `function_name`, `input_type` (first param annotation),
   `return_type` (return annotation via `ast.unparse()`)
4. Walk function body for `inputs.X` attribute accesses -> `input_fields`

Returns `None` if file doesn't exist, has syntax errors, or lacks `run_*`.

### From SysML Model (lines 195-239)

`generate_expected_signature(calc_def:` [`CalculationDefinitionData`](09-data-models.md)`) -> FunctionSignature`

```python
func_name = f"run_{calc_def.name.lower()}"
input_type = f"{calc_def.name}Input"
output_count = len(calc_def.output_attributes)
if output_count == 0:
    return_type = "None"
elif output_count == 1:
    return_type = "float"
else:  # >= 2
    return_type = f"tuple[{', '.join(['float'] * output_count)}]"
input_fields = [attr.name for attr in calc_def.input_attributes]
```

---

## The 4-Case Decision Tree

**File**: `generation/preservation.py:20-61`

`should_regenerate_stencil(calc_def, impl_path) -> tuple[bool, str]`

```
impl_path.exists()?
  |
  +-- No  --> (True, "New module")
  |
  +-- Yes
       |
       extract_signature_from_impl(impl_path) -> sig?
         |
         +-- None  --> (True, "Could not parse")
         |
         +-- sig exists
              |
              sig.matches(expected_sig)?
                |
                +-- True  --> (False, "Signature unchanged")
                |
                +-- False --> (True, "Signature changed")
```

---

## Stub-to-Auto-Impl Upgrade

When `should_regenerate_stencil()` returns `False` (signature unchanged),
a second check determines if a stub can be upgraded:

**File**: `cli/__init__.py:659-691`

```python
if not should_regen:
    existing_content = output_path.read_text()
    is_stub = "raise NotImplementedError" in existing_content
    has_auto_impl = (
        compilation_result is not None
        and compilation_result.overall_compilability == Compilability.FULLY_COMPILABLE
    )
    if is_stub and has_auto_impl:
        backup_implementation(output_path, backup_dir)
        code = generate_implementation(..., compilation_result=result)
        output_path.write_text(code)
```

**Conditions for upgrade**:
1. Signature unchanged (preserve-worthy)
2. File contains `"raise NotImplementedError"` (is a stub)
3. Compilation result is `FULLY_COMPILABLE` (auto-impl available)

Handwritten implementations (without `NotImplementedError`) are never upgraded.

---

## Backup System

**File**: `generation/preservation.py:64-93`

```python
def backup_implementation(impl_path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{impl_path.stem}_{timestamp}.py"
    shutil.copy2(impl_path, backup_dir / backup_name)
    return backup_dir / backup_name
```

Called **before** every regeneration or upgrade. Timestamped for multiple runs.

Example: `handwritten/backup/alphaneutronsplit_impl_20260216_143022.py`

---

## CLI Flags

| Flag | Effect |
|------|--------|
| `--smart-regen` | Selective: compare signatures, preserve if unchanged, upgrade stubs |
| `--preserve-handwritten` | Blanket: preserve ALL existing handwritten files, no comparison |
| Neither | Overwrite everything |

`--preserve-handwritten` does not upgrade stubs and does not use the backup
system. It simply skips generation for any existing `handwritten/*.py` file.

---

## Concrete Scenarios

| Case | Condition | Action |
|------|-----------|--------|
| A: New file | impl doesn't exist | Generate (auto-impl or stub) |
| B: Handwritten, unchanged | matches()=True, no NotImplementedError | **Preserve** |
| C: Stub, compilable | matches()=True, has NotImplementedError, FULLY_COMPILABLE | Backup + upgrade |
| D: Interface changed | matches()=False (return type or fields differ) | Backup + regenerate |

**Limitation**: Smart-regen only works for CalcUsage modules (which have
[`CalculationDefinitionData`](09-data-models.md)). [Aggregation](13-aggregation-scoping.md)
and [computed attribute](16-computed-attributes.md) modules are synthetic — regenerated
every time (REQ-SR-06).

---

## Data Models

| Model | File | Role |
|-------|------|------|
| `FunctionSignature` | `analysis/signature_extractor.py` | Signature comparison |
| `CalculationDefinitionData` | `extraction/data_models.py` | Expected signature source |
| `Compilability` | `extraction/expression_compiler.py` | FULLY_COMPILABLE check ([doc 14](14-expression-compiler.md)) |
| `GenerationConfig` | `cli/__init__.py` | smart_regen, preserve_handwritten flags |

## Related Documents

- **Upstream**: [08-generation](08-generation.md) — generation overview, where smart-regen fits in the output pipeline
- **Upstream**: [14-expression-compiler](14-expression-compiler.md) — `Compilability` enum, determines if auto-impl is available
- **Extraction**: [01-extraction](01-extraction.md) — produces `CalculationDefinitionData` used for expected signatures
- **Schema**: [22-output-schema-rules](22-output-schema-rules.md) — output schema generation that smart-regen protects
- **Module types**: [05-module-factory](05-module-factory.md) — CalcUsage vs synthetic module distinction
- **Data models**: [09-data-models](09-data-models.md) — `CalculationDefinitionData`, `AttributeInfo` definitions
