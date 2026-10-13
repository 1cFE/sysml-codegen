---
id: 0015
title: Study tools anchor the project root to the package's git work tree, with an explicit override
date: 2026-10-12
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (design DD2, approved for planning by the orchestrator, 2026-10-12; narrowed to the root rule roots.py implements, audit F6, 2026-10-12)"
seams: [study, fusion-tea]
supersedes: null
promoted_to: null
---

## Decision

The study tools (`sysml_codegen.study`) cite every path relative to a project root that `study/roots.py` names. The first rule that applies wins: an in-process override (`roots.use_project_root`, for library callers such as fusion-tea's module aliases), then `SYSML_CODEGEN_PROJECT_ROOT`, then a git work tree. On a tool's command line, that work tree is the one containing the package the tool was given, and the tool refuses with exit 2 and writes nothing when the package is in no work tree and neither override is set, or when the working directory is inside a different work tree from the package. A library call uses the working directory's work tree instead and checks no conflict, unless something has pinned the root: `integrate` exports it to every producer, and read coverage pins it from the package before it observes a route.

## Why

- Installed code cannot find the project from its own file, as fusion-tea's copies did with `Path(__file__)`. Some root has to be named.
- A wrong root never raises an error. `manifest.repo_relative_posix` renders a path outside the root with `..` segments, so a wrong root writes plausible, wrong paths into committed documents. That is why the anchor is the package, and why a conflicting working directory is a refusal, not a quiet second answer.
- A study document must have the same bytes from any working directory; fusion-tea's `test_output_contract.py` and `test_identity.py` pin this. Anchoring on the package gives it, and a working directory outside every work tree is not a conflict.
- Nothing can detect a monorepo whose top level is not the modeling project (design KB1). The variable is the remedy there, and the runbook and integration guide say so.

## Invariants established

- A document a tool writes from its command line has paths relative to the project root, the same from any working directory. No root, or a conflicting one, is exit 2 with no document (design I3).
- A library call that nothing has pinned, such as a route that calls `identity.build_sealed` when run by hand, resolves the root from the working directory. Run from inside another repository, it cites paths with `..` segments and nothing compares them. The runbook's "The tools" states this rule.
- `integrate` hands the root it judged to every producer as `SYSML_CODEGEN_PROJECT_ROOT`. Read coverage resolves and pins the root before it observes a route, so a route in a git work tree needs no variable.

## Rejected alternatives

- The working directory alone was rejected: a document's bytes would vary with where the tool runs.
- The git top level of the working directory was rejected: it silently gives a wrong root when an agent stands in another repository.
- The nearest `pyproject.toml` with a `[tool.sysml-codegen]` table was rejected: an undeclared project would have no root at all.
- A `--project-root` flag on each tool was rejected: it changes every recorded `command` argv.
