# 23 -- Smart Regeneration and Implementation Preservation

## The Problem

When the SysML model changes and codegen re-runs, handwritten implementation
files (`handwritten/*_impl.py`) can be overwritten. Smart-regen compares
function signatures to preserve handwritten code when the interface hasn't
changed, and upgrades stubs to auto-implementations when possible.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-SR-01 | Signature comparison SHALL use two-level matching: type-level (required) then field-level (optional) | `FunctionSignature.matches()` in `generation/preservation.py` — the only copy |
| REQ-SR-02 | Field comparison SHALL be order-independent (sorted) | `sorted(self.input_fields) == sorted(other.input_fields)` |
| REQ-SR-03 | `should_regenerate_stencil()` SHALL implement the [6-case decision tree](#the-6-case-decision-tree) | 6 return paths in `should_regenerate_stencil()` (`generation/preservation.py`) — Item 5 split the unparseable leaf into preserve-on-transient / preserve-non-empty / regenerate-empty |
| REQ-SR-04 | Stub upgrade SHALL require all 3 conditions: signature match, `NotImplementedError` present, `auto_impl_context` available | `_generate_stencils()` in `cli/__init__.py` checks all three |
| REQ-SR-05 | Backup SHALL be created before every regeneration or upgrade | `backup_implementation()` called before `write_text()` |
| REQ-SR-06 | Aggregation and [computed-attribute](16-computed-attributes.md) modules are synthetic and always regenerated in practice | The unified `_generate_stencils()` processes all module types; synthetic modules lack handwritten content so the smart-regen path is a no-op |
| REQ-SR-07 | `--preserve-handwritten` SHALL skip ALL existing handwritten files without comparison | Blanket skip, no signature extraction |

---

## FunctionSignature Data Model

**File**: `generation/preservation.py` (`FunctionSignature`). This is the only copy. A parallel
`analysis/signature_extractor.py` used to exist beside it with no production caller; the
recovery deleted it (Gate 4B-G1, `6ba346e`), so the duplication this document used to warn
about is gone.

```python
@dataclass
class FunctionSignature:
    function_name: str              # "run_alphaneutronsplit"
    input_type: str                 # "AlphaNeutronSplitInput"
    return_type: str                # "float" or "tuple[float, float]"
    input_fields: list[str] | None  # ["n_alpha_in", "n_neutron_in"] or None
```

### matches() Method

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

### From Existing File

`_extract_signature_from_impl(impl_path: Path) -> FunctionSignature | None` in
`generation/preservation.py` — this is what the decision tree calls, and the only
implementation.

Uses Python AST to find `run_*` function:
1. Parse source with `ast.parse()`
2. Walk AST for `FunctionDef` nodes starting with `run_`
3. Extract `function_name`, `input_type` (first param annotation),
   `return_type` (return annotation via `ast.unparse()`)
4. Walk function body for `inputs.X` attribute accesses -> `input_fields`

Returns `None` if file doesn't exist, has syntax errors, or lacks `run_*`.

### From PipelineModule

`_generate_expected_signature_from_module(module) -> FunctionSignature`

The decision tree in `preservation.py` derives the expected signature from
`PipelineModule` fields, not directly from `CalculationDefinitionData`:

```python
func_name = f"run_{module.calc_def_name.lower()}"
input_type = f"{module.calc_def_name}Input"
output_count = len(module.outputs)
if output_count == 0:
    return_type = "None"
elif output_count == 1:
    return_type = "float"
else:  # >= 2
    return_type = f"tuple[{', '.join(['float'] * output_count)}]"
input_fields = [inp.param_name for inp in module.inputs]
```

> **Note**: the expected signature is derived from `PipelineModule` on purpose. A
> `generate_expected_signature()` taking `CalculationDefinitionData` directly used to exist in
> `analysis/signature_extractor.py`; deriving from the graph rather than from extraction data
> is what REQ-PIPE-07 asks for, and the extraction-fed version had no caller and is gone.

---

## The 6-Case Decision Tree

**File**: `generation/preservation.py` (`should_regenerate_stencil()`)

`should_regenerate_stencil(module, impl_path) -> tuple[bool, str]`

Item 5 (D3-14, preserve-on-transient, INV-4) split the old `None -> (True, "Could
not parse")` leaf into three outcomes: a transient read/parse failure on a
**non-empty** impl now PRESERVES the handwritten file (never stubs over it), and
only a genuinely-empty impl regenerates.

```
impl_path.exists()?
  |
  +-- No  --> (True, "New module")
  |
  +-- Yes
       |
       _extract_signature_from_impl(impl_path) -> sig?
         |
         +-- None (could not extract a signature)
         |     |
         |     +-- OSError reading the file --> (False, "Preserved on transient read error")
         |     +-- file has non-empty content --> (False, "Preserved (non-empty, unparseable — transient)")
         |     +-- file is empty              --> (True,  "Empty implementation (nothing to preserve)")
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

**File**: `cli/__init__.py` (within `_generate_stencils()`)

```python
if not should_regen:
    existing_content = output_path.read_text()
    is_stub = "raise NotImplementedError" in existing_content
    has_auto_impl = module.auto_impl_context is not None
    if is_stub and has_auto_impl:
        backup_implementation(output_path, backup_dir)
        code = generate_implementation(
            module, template_env, output_path, config.package_name,
        )
        if code:
            output_path.write_text(code)
```

**Conditions for upgrade**:
1. Signature unchanged (preserve-worthy)
2. File contains `"raise NotImplementedError"` (is a stub)
3. `module.auto_impl_context` is not `None` (auto-impl available)

Handwritten implementations (without `NotImplementedError`) are never upgraded.

---

## Backup System

**File**: `generation/preservation.py` (`backup_implementation()`)

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
| C: Stub, compilable | matches()=True, has NotImplementedError, `auto_impl_context` present | Backup + upgrade |
| D: Interface changed | matches()=False (return type or fields differ) | Backup + regenerate |

**Limitation**: Smart-regen is primarily meaningful for CalcUsage modules
(which have user-editable handwritten files). [Aggregation](13-aggregation-scoping.md)
and [computed attribute](16-computed-attributes.md) modules are synthetic --
they pass through the same unified `_generate_stencils()` loop but in practice
are always regenerated since they lack handwritten content (REQ-SR-06).

---

## Data Models

| Model | File | Role |
|-------|------|------|
| `FunctionSignature` | `generation/preservation.py` | Signature comparison |
| `PipelineModule` | `resolution/models.py` | Expected signature source (via `calc_def_name`, `inputs`, `outputs`) |
| `Compilability` | `extraction/expression_compiler.py` | Upstream enum; stub upgrade checks `module.auto_impl_context` ([doc 14](14-expression-compiler.md)) |
| `GenerationConfig` | `cli/__init__.py` | smart_regen, preserve_handwritten flags |

## Related Documents

- **Upstream**: [08-generation](08-generation.md) — generation overview, where smart-regen fits in the output pipeline
- **Upstream**: [14-expression-compiler](14-expression-compiler.md) — `Compilability` enum, determines if auto-impl is available
- **Extraction**: [01-extraction](01-extraction.md) — produces `CalculationDefinitionData` used for expected signatures
- **Schema**: [22-output-schema-rules](22-output-schema-rules.md) — output schema generation that smart-regen protects
- **Module types**: [05-module-factory](05-module-factory.md) — CalcUsage vs synthetic module distinction
- **Data models**: [09-data-models](09-data-models.md) — `CalculationDefinitionData`, `AttributeInfo` definitions
