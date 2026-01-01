# TEAx Completion Command

**Purpose**: Implement physics calculations from generated code stencils
**Input**: `{package}/IMPLEMENTATION_BACKLOG.md`
**Output**: Completed `{package}/handwritten/*_impl.py` files

## Instructions

You are a specialist physics modeling and simulation agent. Your job is to complete and verify a TEA simulation library. You will be given very clear instructions on what is remaining to be done.

**Context**: Before starting, read:
- USER_README.md (if exists)
- models/README.md
- /home/reid/teax/TEAX_README.md

## Pre-Check: Discover Package

**Find the generated package**:
```python
Glob(pattern="*/IMPLEMENTATION_BACKLOG.md")
```

The directory containing `IMPLEMENTATION_BACKLOG.md` is your `{package}`.

If multiple packages found:
```python
AskUserQuestion(
  questions=[{
    "question": "Multiple packages found. Which should I complete?",
    "header": "Package",
    "options": [
      {"label": "{pkg1}", "description": "Complete {pkg1}"},
      {"label": "{pkg2}", "description": "Complete {pkg2}"}
    ],
    "multiSelect": False
  }]
)
```

If no packages found:
```markdown
No IMPLEMENTATION_BACKLOG.md found.
Code generation may not have completed successfully.
Please run the codegen pipeline first:
  sysml-codegen generate --models <path> --output <dir>
```

## Pre-Check: Verify Codegen Complete

Before starting implementation, verify code generation completed:

1. Check that `{package}/IMPLEMENTATION_BACKLOG.md` exists
2. Check that `{package}/inputs/*.json` files exist and contain non-null values
3. Check that `{package}/schemas/*_params.py` files exist

If any missing or inputs contain null values, STOP:
> "Code generation appears incomplete. Please run the full codegen pipeline
> including Phase B (`generate_scenario.py --generate-inputs`) before proceeding."

**Current Stage**:
1. We have aligned on SysMLv2 models in `models/`
2. We have run the initial code generation process
3. We have NOT finished the `{package}/` code.

**Your task**: Read and follow ALL instructions in `{package}/IMPLEMENTATION_BACKLOG.md`

The backlog document contains:
- **Stage 1**: Function implementations (table with SysML sources)
- **Stage 2**: Verification testing

*Note: Schemas are auto-generated from SysML models. See `{package}/schemas/*_params.py` and `*_output.py`.*

## Process

1. Open `{package}/IMPLEMENTATION_BACKLOG.md` and read completely
2. Follow each stage in order
3. ALWAYS mark off items in the `IMPLEMENTATION_BACKLOG.md` as you complete them
4. Use TodoWrite to track progress through the implementations
5. If unable to resolve issues, note in `IMPLEMENTATION_BACKLOG.md` and continue

## Done Criteria

ALL items in IMPLEMENTATION_BACKLOG.md completed:
- Stage 1 complete (All functions implemented, no NotImplementedError)
- Stage 2 complete (all verification tests pass)
- Runnable tests pass (`pytest {package}/tests/test_implementations_runnable.py`)

---

**Last Updated**: 2026-01-01
