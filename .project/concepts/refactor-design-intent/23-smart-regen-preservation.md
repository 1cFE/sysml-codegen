# 23 -- Smart Regeneration and Implementation Preservation

## The Problem

When the SysML model changes and codegen re-runs, handwritten implementation
files (`handwritten/*_impl.py`) can be overwritten. Smart-regen compares
function signatures to preserve handwritten code when the interface hasn't
changed, and upgrades stubs to auto-implementations when possible.

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

`generate_expected_signature(calc_def: CalculationDefinitionData) -> FunctionSignature`

```python
func_name = f"run_{calc_def.name.lower()}"
input_type = f"{calc_def.name}Input"
if len(calc_def.output_attributes) == 1:
    return_type = "float"
elif len(calc_def.output_attributes) >= 2:
    return_type = f"tuple[{', '.join(['float'] * len(calc_def.output_attributes))}]"
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

## Concrete Scenario Trace

**Model**: CalcDef `AlphaNeutronSplit` with 2 inputs, 2 outputs.

**Case A: New file** -- `handwritten/alphaneutronsplit_impl.py` doesn't exist.
- `should_regenerate_stencil()` -> `(True, "New module")`
- Generate auto-impl (if FULLY_COMPILABLE) or stub

**Case B: Handwritten, unchanged** -- Developer wrote custom logic.
- Extract signature from file: `run_alphaneutronsplit(inputs: AlphaNeutronSplitInput) -> tuple[float, float]`
- `matches(expected)` -> `True`
- `is_stub` -> `False` (no NotImplementedError)
- **Preserved**, no backup needed.

**Case C: Stub, auto-impl available** -- Stub exists, model now compilable.
- `matches(expected)` -> `True` (stubs have same signature)
- `is_stub` -> `True`
- `has_auto_impl` -> `True` (FULLY_COMPILABLE)
- Backup stub, write auto-impl.

**Case D: Interface changed** -- SysML added an output attribute.
- Extract: `return_type = "tuple[float, float]"` (old)
- Expected: `return_type = "tuple[float, float, float]"` (new, 3 outputs)
- `matches()` -> `False` (return type differs)
- `should_regenerate_stencil()` -> `(True, "Signature changed")`
- Backup old file, regenerate.

---

## Important Limitation

Smart-regen compares against `CalculationDefinitionData`, which only exists
for CalcUsage modules. Aggregation modules and computed attribute modules
are synthetic -- they have no CalcDef and are not covered by smart-regen.
These modules are regenerated every time.

---

## Data Models

| Model | File | Role |
|-------|------|------|
| `FunctionSignature` | `analysis/signature_extractor.py` | Signature comparison |
| `CalculationDefinitionData` | `extraction/data_models.py` | Expected signature source |
| `Compilability` | `extraction/expression_compiler.py` | FULLY_COMPILABLE check |
| `GenerationConfig` | `cli/__init__.py` | smart_regen, preserve_handwritten flags |
