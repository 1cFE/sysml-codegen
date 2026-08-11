# ELABORATE-FIRST Item 7 Cutover Census

- **Status:** DR3 bounded corrections applied; generated closure evidence passes; focused rereview pending
- **Owner:** Reid W
- **Captured:** 2026-08-10
- **Repositories:** `sysml-codegen` and `../agentic-mbse`
- **Codegen baseline:** branch `source-identity-epic`, commit `1672c57`, certified Item-6 dirty state
- **Authority:** dispositions are design decisions derived from
  [spec.md](spec.md); they remain subject to the spec's pending owner recapture gate

This is the durable R3/R6 census. A row may be split during planning, but it may not disappear,
change disposition, or gain a compatibility path without amending the design. There are no
unresolved disposition rows.

## Closure Method

The census was populated from the certified dirty trees with these exact discovery commands. The
checked-in `.project/active/elaborator-cutover/cutover-inventory.json` is generated, not hand-written.
Its repository entries truthfully use `comparison_basis: "current-worktree"` and
`exact_base_comparison: false` while the certified Item-6 trees are dirty; this proves the current
affected set and byte identities, but it cannot claim a clean-base comparison. These commands create
and check it:

```bash
rg --files src/sysml_codegen tests scripts docs | LC_ALL=C sort
git -C ../agentic-mbse ls-files 'src/**' 'tests/**' | LC_ALL=C sort
rg -n 'build_pipeline_context|build_elaborated_pipeline|capture_snapshot|build_pipeline_context_from_snapshot|PipelineContext' src tests scripts
rg -n 'PartInstanceIndex|PathStep|InstanceOccurrence|DependencyBacktracker|OutputRegistry|build_output_registry|build_computation_graph|collect_uncovered_params' src tests scripts
rg -n 'build_full_graph_from_snapshot|build_classifier_inputs_from_snapshot|load_extraction_snapshot|serialize_extraction_snapshot|snapshot_to_json|GrandfatheredSnapshotError|constraint_lowering_mode' src tests scripts
rg -n 'compile_calc_def_exact|compile_calc_def|extract_constraint_facts|PROFILE_SEMANTIC_VERSION|EXPRESSION_IR_SCHEMA_VERSION' src ../agentic-mbse/src tests ../agentic-mbse/tests
rg -n 'in [A-Za-z_][A-Za-z0-9_]*\s*=\s*[A-Za-z_][A-Za-z0-9_]*' tests/fixtures/fusion_tea --glob '*.sysml'
rg -n 'extract_identified_constraint_facts|evaluate_identified_profile|evaluate_profile|preflight' ../agentic-mbse/src ../agentic-mbse/tests
.venv/bin/python scripts/check_cutover_census.py inventory --census .project/active/elaborator-cutover/cutover-census.md --repo codegen=. --repo agentic=../agentic-mbse --write .project/active/elaborator-cutover/cutover-inventory.json
.venv/bin/python scripts/check_cutover_census.py compare --census .project/active/elaborator-cutover/cutover-census.md --inventory .project/active/elaborator-cutover/cutover-inventory.json --require-sorted --require-closed
.venv/bin/python scripts/check_cutover_residue.py --repo codegen=. --repo agentic=../agentic-mbse --inventory .project/active/elaborator-cutover/cutover-inventory.json --rule all --expect inventoried
```

`cutover-inventory/v1` is exact JSON with keys `schema`, `generated_from`, `repositories`, and
`rows`. Repositories bind real path, HEAD, dirty-state hash, comparison basis, and whether exact-base
comparison was possible. Rows are
strictly sorted by `(repo,path,symbol_or_command,responsibility_id)` and each has exact keys
`id`, `repo`, `path`, `kind`, `symbol_or_command`, `responsibility_id`, `status`, `current_owner`,
`disposition`, `final_owner`, `replacement_test`, `residue_gate`, plus generated `sha256`,
`size_bytes`, and `worktree_state`. Current `kind` values are
`production|documentation|workflow|script|test|test-helper|fixture|golden|artifact`. Every policy
value is nonempty; disposition
is `delete|migrate|retain`; row key `(repo,path,symbol_or_command,responsibility_id)` is unique.

The inventory scanner enumerates `git ls-files --cached --others --exclude-standard` in both
repositories and scans every non-project text file for the policy's self-safe Unicode marker table.
The explicit policy rows add path/symbol responsibilities such as goldens and generated-call fallout
that a symbol scan cannot infer. `compare` computes exact row equality between the embedded policy
and generated inventory. An affected marker path absent from the policy, missing existing path,
extra row, duplicate, unsorted row, blank field, or unresolved disposition fails.
Grouped census rows are legal only when every explicit member has identical responsibility,
disposition, final owner, replacement, and gate. Divergent members use child IDs.

The spec, reviews, Item-6 plan/audit/research, shared design, 29-cell contract, and Item-5 ledger
close behavioral owners that imports cannot identify. The scanner's banned-symbol table stores each
name as Unicode code points and reconstructs it at runtime; the oracle source therefore contains no
plain banned token. It tokenizes Python, parses AST attributes/imports, and scans non-Python text
while excluding `.project/**`, `.git/**`, its own file, the canonical candidate/acceptance JSON, and
historical evidence. Encoded oracle literals are classified separately from executable residue.

DR3 closure evidence on 2026-08-10: the two checker unit files passed `4/4`; inventory generation
found 78 marker-discovered paths and wrote 231 sorted stable rows; compare returned
`{"closed":true,"rows":231,"sorted":true}`. The self-safe current-worktree residue gates returned
363 inventoried hits for `all` and five inventoried hits for `item6-dual-2`. These are transitional
census results, not final absence results. The implementation candidate must rerun the same rules
with `--expect absent` after deletion/migration.

Disposition vocabulary:

- **DELETE:** remove the files/symbols/tests. No compatibility alias or reconstructing adapter.
- **MIGRATE:** preserve the capability or oracle at the named sole-authority owner.
- **RETAIN:** keep a positive exact or route-neutral responsibility. It must pass the row's
  non-reconstruction proof.

<!-- cutover-inventory-policy:v1
{
  "schema": "cutover-inventory-policy/v1",
  "markers": [
    [
      79,
      117,
      116,
      112,
      117,
      116,
      82,
      101,
      103,
      105,
      115,
      116,
      114,
      121
    ]
  ],
  "rows": [
    {
      "id": "INV-CG-CENSUS-SCRIPT",
      "repo": "codegen",
      "path": "scripts/check_cutover_census.py",
      "kind": "script",
      "symbol_or_command": "inventory/compare CLI",
      "responsibility_id": "SCR-07",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "retain",
      "final_owner": "generated inventory owner",
      "replacement_test": "CUT-CENSUS-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-CG-CENSUS-TEST",
      "repo": "codegen",
      "path": "tests/unit/test_check_cutover_census.py",
      "kind": "test",
      "symbol_or_command": "inventory checker contract",
      "responsibility_id": "SCR-07",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "retain",
      "final_owner": "generated inventory proof",
      "replacement_test": "CUT-CENSUS-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-CG-RESIDUE-SCRIPT",
      "repo": "codegen",
      "path": "scripts/check_cutover_residue.py",
      "kind": "script",
      "symbol_or_command": "structural residue CLI",
      "responsibility_id": "SCR-08",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "retain",
      "final_owner": "self-safe residue owner",
      "replacement_test": "CUT-RESIDUE-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-CG-RESIDUE-TEST",
      "repo": "codegen",
      "path": "tests/unit/test_check_cutover_residue.py",
      "kind": "test",
      "symbol_or_command": "residue checker contract",
      "responsibility_id": "SCR-08",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "retain",
      "final_owner": "self-safe residue proof",
      "replacement_test": "CUT-RESIDUE-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-CG-FT-IFE",
      "repo": "codegen",
      "path": "tests/fixtures/fusion_tea/library/analyses/ife_lcoe.sysml",
      "kind": "fixture",
      "symbol_or_command": "FTGEN-01 through FTGEN-07",
      "responsibility_id": "FIX-01/FTGEN-01..07",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "migrate",
      "final_owner": "maintained Fusion Tea model",
      "replacement_test": "CUT-FT-01/CUT-ARITH-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-CG-FT-CYCLE",
      "repo": "codegen",
      "path": "tests/fixtures/fusion_tea/library/analyses/fusion_cycle.sysml",
      "kind": "fixture",
      "symbol_or_command": "FTGEN-08 through FTGEN-10",
      "responsibility_id": "FIX-01/FTGEN-08..10",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "migrate",
      "final_owner": "maintained Fusion Tea model",
      "replacement_test": "CUT-FT-01/CUT-ARITH-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-CG-FT-HIF",
      "repo": "codegen",
      "path": "tests/fixtures/fusion_tea/library/analyses/hif_economics.sysml",
      "kind": "fixture",
      "symbol_or_command": "FTGEN-11 through FTGEN-15",
      "responsibility_id": "FIX-01/FTGEN-11..15",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "migrate",
      "final_owner": "maintained Fusion Tea model",
      "replacement_test": "CUT-FT-01/CUT-ARITH-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-CG-FT-CALLER",
      "repo": "codegen",
      "path": "tests/runtime/test_fusion_tea_acceptance.py",
      "kind": "test",
      "symbol_or_command": "FTGEN-08/09/14/15 direct run calls",
      "responsibility_id": "FTGEN-08/09/14/15",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "migrate",
      "final_owner": "real public TEAx proof",
      "replacement_test": "CUT-TEAX-01/CUT-ARITH-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-CG-GOLDEN-COMP",
      "repo": "codegen",
      "path": "tests/fixtures/golden/calc_def_compilation_golden.json",
      "kind": "golden",
      "symbol_or_command": "15 affected arithmetic result records",
      "responsibility_id": "GOLDEN-01",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "migrate",
      "final_owner": "exact compiler arithmetic oracle",
      "replacement_test": "CUT-ARITH-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-CG-GOLDEN-PARITY",
      "repo": "codegen",
      "path": "tests/fixtures/golden/calc_compat_parity_golden.json",
      "kind": "golden",
      "symbol_or_command": "3 changed records and 3 controls",
      "responsibility_id": "GOLDEN-02",
      "status": "existing",
      "current_owner": "current affected surface",
      "disposition": "migrate",
      "final_owner": "independent arithmetic controls",
      "replacement_test": "CUT-ARITH-01",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-CANDIDATE-SCRIPT",
      "repo": "codegen",
      "path": "scripts/check_cutover_candidate.py",
      "kind": "script",
      "symbol_or_command": "singular coordinator CLI",
      "responsibility_id": "SCR-06",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-CANDIDATE-UNIT",
      "repo": "codegen",
      "path": "tests/unit/test_check_cutover_candidate.py",
      "kind": "test",
      "symbol_or_command": "candidate identity tests",
      "responsibility_id": "PROMO-02",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-CANDIDATE-INTEGRATION",
      "repo": "codegen",
      "path": "tests/integration/test_cutover_candidate_promotion.py",
      "kind": "test",
      "symbol_or_command": "authoritative remote CAS tests",
      "responsibility_id": "PROMO-03",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-CANDIDATE-WORKFLOW-TEST",
      "repo": "codegen",
      "path": "tests/conformance/test_cutover_candidate_workflows.py",
      "kind": "test",
      "symbol_or_command": "ruleset/workflow tests",
      "responsibility_id": "PROMO-04",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-CG-BRANCH-WORKFLOW",
      "repo": "codegen",
      "path": ".github/workflows/elaborator-cutover-branch.yml",
      "kind": "workflow",
      "symbol_or_command": "protected branch caller",
      "responsibility_id": "PROMO-07",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-AG-BRANCH-WORKFLOW",
      "repo": "agentic",
      "path": ".github/workflows/elaborator-cutover-branch.yml",
      "kind": "workflow",
      "symbol_or_command": "reciprocal branch caller",
      "responsibility_id": "PROMO-08",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-CG-TAG-WORKFLOW",
      "repo": "codegen",
      "path": ".github/workflows/elaborator-cutover-tags.yml",
      "kind": "workflow",
      "symbol_or_command": "paired product-tag publisher",
      "responsibility_id": "PROMO-09",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-AG-TAG-WORKFLOW",
      "repo": "agentic",
      "path": ".github/workflows/elaborator-cutover-tags.yml",
      "kind": "workflow",
      "symbol_or_command": "reciprocal tag caller",
      "responsibility_id": "PROMO-10",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-CG-RELEASE-WORKFLOW",
      "repo": "codegen",
      "path": ".github/workflows/elaborator-cutover-release.yml",
      "kind": "workflow",
      "symbol_or_command": "release gate caller",
      "responsibility_id": "PROMO-11",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-AG-RELEASE-WORKFLOW",
      "repo": "agentic",
      "path": ".github/workflows/elaborator-cutover-release.yml",
      "kind": "workflow",
      "symbol_or_command": "reciprocal release caller",
      "responsibility_id": "PROMO-12",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-CANDIDATE-RECORD",
      "repo": "codegen",
      "path": ".project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json",
      "kind": "artifact",
      "symbol_or_command": "singular paired candidate record",
      "responsibility_id": "PROMO-01",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-PLAN-RELEASE-MANIFEST",
      "repo": "codegen",
      "path": ".project/active/elaborator-cutover/evidence/release-manifest.json",
      "kind": "artifact",
      "symbol_or_command": "paired release manifest",
      "responsibility_id": "PROMO-19",
      "status": "planned",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion protocol",
      "replacement_test": "CUT-PROMO-01/02/03",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-RUNTIME-JOURNAL",
      "repo": "coordination",
      "path": "<state-dir>/<candidate_id>/promotion-journal.json",
      "kind": "artifact",
      "symbol_or_command": "durable promotion journal",
      "responsibility_id": "PROMO-05",
      "status": "runtime",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion coordinator",
      "replacement_test": "CUT-PROMO-02",
      "residue_gate": "NR-13"
    },
    {
      "id": "INV-RUNTIME-LOCK",
      "repo": "coordination",
      "path": "<state-dir>/elaborator-cutover-promotion.lock",
      "kind": "artifact",
      "symbol_or_command": "cross-repository promotion lock",
      "responsibility_id": "PROMO-06",
      "status": "runtime",
      "current_owner": "none",
      "disposition": "retain",
      "final_owner": "paired promotion coordinator",
      "replacement_test": "CUT-PROMO-02",
      "residue_gate": "NR-13"
    },
  {
    "id": "INV-DISC-001",
    "repo": "codegen",
    "path": "docs/architecture/overview.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-002",
    "repo": "codegen",
    "path": "docs/architecture/reference/00-pipeline-overview.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-003",
    "repo": "codegen",
    "path": "docs/architecture/reference/02-orchestration.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-004",
    "repo": "codegen",
    "path": "docs/architecture/reference/03-resolution-overview.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-005",
    "repo": "codegen",
    "path": "docs/architecture/reference/04-producer-resolution.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-006",
    "repo": "codegen",
    "path": "docs/architecture/reference/06-entry-point-classifier.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-007",
    "repo": "codegen",
    "path": "docs/architecture/reference/09-data-models.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-008",
    "repo": "codegen",
    "path": "docs/architecture/reference/10-output-registry.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-009",
    "repo": "codegen",
    "path": "docs/architecture/reference/11-analysis-backtracker.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-010",
    "repo": "codegen",
    "path": "docs/architecture/reference/12-virtual-binding-rewrite.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-011",
    "repo": "codegen",
    "path": "docs/architecture/reference/13-aggregation-scoping.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-012",
    "repo": "codegen",
    "path": "docs/architecture/reference/15-naming-conventions.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-013",
    "repo": "codegen",
    "path": "docs/architecture/reference/16-computed-attributes.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-014",
    "repo": "codegen",
    "path": "docs/architecture/reference/19-ast-dispatch-invariant.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-015",
    "repo": "codegen",
    "path": "docs/architecture/reference/24-dual-resolution-architecture.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-016",
    "repo": "codegen",
    "path": "docs/architecture/verification-matrix.md",
    "kind": "documentation",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-017",
    "repo": "codegen",
    "path": "scripts/spike_agg_wiring_h1_h4.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-018",
    "repo": "codegen",
    "path": "scripts/spike_aggregation_validation.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-019",
    "repo": "codegen",
    "path": "scripts/spike_backtracker_resolution_paths.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-020",
    "repo": "codegen",
    "path": "scripts/spike_c11b_typed_dispatch.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-021",
    "repo": "codegen",
    "path": "scripts/spikes/spike_bare_name_collisions.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-022",
    "repo": "codegen",
    "path": "scripts/spikes/spike_chain_redef_rhs.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-023",
    "repo": "codegen",
    "path": "scripts/spikes/spike_expose_pure_chain.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-024",
    "repo": "codegen",
    "path": "scripts/spikes/spike_issue22_agg_ref.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-025",
    "repo": "codegen",
    "path": "scripts/spikes/spike_output_registry_e2e.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-026",
    "repo": "codegen",
    "path": "scripts/spikes/spike_reference_resolution.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-027",
    "repo": "codegen",
    "path": "scripts/spikes/spike_virtual_instance_keys.py",
    "kind": "script",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "kept exact tests/research",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-028",
    "repo": "codegen",
    "path": "src/sysml_codegen/analysis/constraint_lowering.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-15",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "neutral exact helpers",
    "replacement_test": "CUT-CON-01/CUT-PROJ-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-029",
    "repo": "codegen",
    "path": "src/sysml_codegen/analysis/dependency_backtracker.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-06",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "typed-edge target closure",
    "replacement_test": "CUT-SEL-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-030",
    "repo": "codegen",
    "path": "src/sysml_codegen/core/__init__.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-05/09/11",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "exact graph/projector DTO owner",
    "replacement_test": "CUT-PROJ-01/CUT-REG-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-031",
    "repo": "codegen",
    "path": "src/sysml_codegen/core/identifier_types.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-05/09/11",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "exact graph/projector DTO owner",
    "replacement_test": "CUT-PROJ-01/CUT-REG-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-032",
    "repo": "codegen",
    "path": "src/sysml_codegen/core/models.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-05/09/11",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "exact graph/projector DTO owner",
    "replacement_test": "CUT-PROJ-01/CUT-REG-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-033",
    "repo": "codegen",
    "path": "src/sysml_codegen/core/output_registry.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-09/10",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "exact graph/projector",
    "replacement_test": "CUT-REG-01/CUT-PROJ-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-034",
    "repo": "codegen",
    "path": "src/sysml_codegen/extraction/computed_attribute_extractor.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-05/09/11",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "exact graph/projector DTO owner",
    "replacement_test": "CUT-PROJ-01/CUT-REG-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-035",
    "repo": "codegen",
    "path": "src/sysml_codegen/orchestration/output_registry_builder.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-09/10",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "exact graph/projector",
    "replacement_test": "CUT-REG-01/CUT-PROJ-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-036",
    "repo": "codegen",
    "path": "src/sysml_codegen/orchestration/pipeline_builder.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-01/API-01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "sole exact live builder",
    "replacement_test": "CUT-API-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-037",
    "repo": "codegen",
    "path": "src/sysml_codegen/orchestration/pipeline_context.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "API-02",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "builder-created verified context",
    "replacement_test": "CUT-API-02/CUT-REC-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-038",
    "repo": "codegen",
    "path": "src/sysml_codegen/resolution/graph_builder.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-09/10",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "exact graph/projector",
    "replacement_test": "CUT-REG-01/CUT-PROJ-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-039",
    "repo": "codegen",
    "path": "src/sysml_codegen/resolution/producer_resolution.py",
    "kind": "production",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "PROD-07",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "exact graph/projector",
    "replacement_test": "CUT-REG-01/CUT-PROJ-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-040",
    "repo": "codegen",
    "path": "tests/conformance/test_agg_key_forms.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-041",
    "repo": "codegen",
    "path": "tests/conformance/test_backtracker.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-042",
    "repo": "codegen",
    "path": "tests/conformance/test_computed_attributes.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-043",
    "repo": "codegen",
    "path": "tests/conformance/test_constraint_pipeline_threading.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-044",
    "repo": "codegen",
    "path": "tests/conformance/test_data_models.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-01.03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-01.03",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-045",
    "repo": "codegen",
    "path": "tests/conformance/test_dead_code_removal.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-046",
    "repo": "codegen",
    "path": "tests/conformance/test_dm08_enforced_surface.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-047",
    "repo": "codegen",
    "path": "tests/conformance/test_dual_resolution.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-048",
    "repo": "codegen",
    "path": "tests/conformance/test_factory_aggregation.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-049",
    "repo": "codegen",
    "path": "tests/conformance/test_factory_calc_usage.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04.01",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04.01",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-050",
    "repo": "codegen",
    "path": "tests/conformance/test_factory_formula.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-051",
    "repo": "codegen",
    "path": "tests/conformance/test_orchestrator.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-052",
    "repo": "codegen",
    "path": "tests/conformance/test_output_registry.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-053",
    "repo": "codegen",
    "path": "tests/conformance/test_producer_completeness_acceptance.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-054",
    "repo": "codegen",
    "path": "tests/conformance/test_silent_failure_sc4a1.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-055",
    "repo": "codegen",
    "path": "tests/fixtures/deep_cross_scope_probe/library.sysml",
    "kind": "fixture",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04.04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent exact fixture",
    "replacement_test": "CUT-PROJ-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-056",
    "repo": "codegen",
    "path": "tests/helpers/registry_compat.py",
    "kind": "test-helper",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-06",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "delete",
    "final_owner": "public exact route",
    "replacement_test": "CUT-TEAX-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-057",
    "repo": "codegen",
    "path": "tests/integration/test_bug2_regression.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-058",
    "repo": "codegen",
    "path": "tests/integration/test_computed_attribute_pipeline.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-059",
    "repo": "codegen",
    "path": "tests/integration/test_e2e_output_registry.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-060",
    "repo": "codegen",
    "path": "tests/integration/test_hierarchy_e2e.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-061",
    "repo": "codegen",
    "path": "tests/integration/test_output_registry_smoke.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-062",
    "repo": "codegen",
    "path": "tests/unit/test_backtracker_aggregation.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-063",
    "repo": "codegen",
    "path": "tests/unit/test_backtracker_computed_attrs.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-064",
    "repo": "codegen",
    "path": "tests/unit/test_constraint_resolver.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-065",
    "repo": "codegen",
    "path": "tests/unit/test_dependency_backtracker.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-066",
    "repo": "codegen",
    "path": "tests/unit/test_graph_builder.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-067",
    "repo": "codegen",
    "path": "tests/unit/test_graph_builder_aggregation.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-068",
    "repo": "codegen",
    "path": "tests/unit/test_graph_builder_computed_attrs.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-069",
    "repo": "codegen",
    "path": "tests/unit/test_hygiene_tail_agg_compile.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04.02",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04.02",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-070",
    "repo": "codegen",
    "path": "tests/unit/test_matcher_fixes_item7.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04.03",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04.03",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-071",
    "repo": "codegen",
    "path": "tests/unit/test_output_aliases.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-072",
    "repo": "codegen",
    "path": "tests/unit/test_output_registry.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-073",
    "repo": "codegen",
    "path": "tests/unit/test_output_registry_construction.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-074",
    "repo": "codegen",
    "path": "tests/unit/test_producer_completeness.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-075",
    "repo": "codegen",
    "path": "tests/unit/test_producer_qn_rule.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-076",
    "repo": "codegen",
    "path": "tests/unit/test_producer_resolution_table.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-077",
    "repo": "codegen",
    "path": "tests/unit/test_silent_failure_family3.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
  },
  {
    "id": "INV-DISC-078",
    "repo": "codegen",
    "path": "tests/unit/test_warning_reconciliation.py",
    "kind": "test",
    "symbol_or_command": "checker-discovered affected path",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current legacy/transition surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-04",
    "replacement_test": "CUT-PROJ-01/CUT-ABS-01",
    "residue_gate": "NR-13"
    },
  {
    "id": "INV-RES-AG-001",
    "repo": "agentic",
    "path": "src/agentic_mbse/sysml/executable_profile.py",
    "kind": "production",
    "symbol_or_command": "_evaluate_usage",
    "responsibility_id": "PROD-20/21",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "sole unsuffixed identified fact/profile route",
    "replacement_test": "CUT-CON-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-AG-002",
    "repo": "agentic",
    "path": "tests/test_sysml/test_constraint_extraction_ordering.py",
    "kind": "test",
    "symbol_or_command": "evaluate_identified_profile, extract_identified_constraint_facts",
    "responsibility_id": "AGENTIC-TEST-01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "identified exact fact/profile test",
    "replacement_test": "CUT-CON-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-AG-003",
    "repo": "agentic",
    "path": "tests/test_sysml/test_executable_profile.py",
    "kind": "test",
    "symbol_or_command": "evaluate_identified_profile",
    "responsibility_id": "AGENTIC-TEST-02",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "identified exact fact/profile test",
    "replacement_test": "CUT-CON-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-AG-004",
    "repo": "agentic",
    "path": "tests/test_sysml/test_public_api_exports.py",
    "kind": "test",
    "symbol_or_command": "extract_identified_constraint_facts",
    "responsibility_id": "AGENTIC-TEST-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "identified exact fact/profile test",
    "replacement_test": "CUT-CON-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-001",
    "repo": "codegen",
    "path": "CLAUDE.md",
    "kind": "documentation",
    "symbol_or_command": "DependencyBacktracker, build_computation_graph",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-002",
    "repo": "codegen",
    "path": "docs/architecture/reference/07-graph-assembly.md",
    "kind": "documentation",
    "symbol_or_command": "DependencyBacktracker, build_computation_graph, build_full_graph_from_snapshot, collect_uncovered_params",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-003",
    "repo": "codegen",
    "path": "docs/architecture/reference/18-literal-value-propagation.md",
    "kind": "documentation",
    "symbol_or_command": "build_computation_graph, rewrite_virtual_bindings",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-004",
    "repo": "codegen",
    "path": "docs/architecture/reference/25-hierarchy-resolver.md",
    "kind": "documentation",
    "symbol_or_command": "supplied_values",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-005",
    "repo": "codegen",
    "path": "docs/architecture/reference/27-snapshot-generation.md",
    "kind": "documentation",
    "symbol_or_command": "build_full_graph_from_snapshot, constraint_lowering_mode, load_extraction_snapshot",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-006",
    "repo": "codegen",
    "path": "docs/architecture/reference/30-diagnostic-severity.md",
    "kind": "documentation",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "DOC-01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "post-cutover architecture documentation",
    "replacement_test": "CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-007",
    "repo": "codegen",
    "path": "scripts/_q5_debug.py",
    "kind": "script",
    "symbol_or_command": "build_output_registry, load_extraction_snapshot",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "exact test/research owner",
    "replacement_test": "CUT-V6-03/CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-008",
    "repo": "codegen",
    "path": "scripts/capture_baseline_yaml.py",
    "kind": "script",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "SCR-02",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "v6 capture driver",
    "replacement_test": "CUT-V6-03/CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-009",
    "repo": "codegen",
    "path": "scripts/capture_extraction_snapshots.py",
    "kind": "script",
    "symbol_or_command": "serialize_extraction_snapshot",
    "responsibility_id": "SCR-02",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "v6 capture driver",
    "replacement_test": "CUT-V6-03/CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-010",
    "repo": "codegen",
    "path": "scripts/capture_pipeline_baselines.py",
    "kind": "script",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "SCR-02",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "v6 capture driver",
    "replacement_test": "CUT-V6-03/CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-011",
    "repo": "codegen",
    "path": "scripts/probes/probe_item4_gate3.py",
    "kind": "script",
    "symbol_or_command": "producer_resolution",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "exact test/research owner",
    "replacement_test": "CUT-V6-03/CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-012",
    "repo": "codegen",
    "path": "scripts/run_elaboration_corpus.py",
    "kind": "script",
    "symbol_or_command": "build_elaborated_pipeline",
    "responsibility_id": "SCR-01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "exact test/research owner",
    "replacement_test": "CUT-V6-03/CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-013",
    "repo": "codegen",
    "path": "scripts/run_phase3.sh",
    "kind": "script",
    "symbol_or_command": "DependencyBacktracker",
    "responsibility_id": "SCR-04",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "exact test/research owner",
    "replacement_test": "CUT-V6-03/CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-014",
    "repo": "codegen",
    "path": "scripts/spike_c12_input_resolver.py",
    "kind": "script",
    "symbol_or_command": "DependencyBacktracker, build_output_registry, load_extraction_snapshot",
    "responsibility_id": "SCR-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "exact test/research owner",
    "replacement_test": "CUT-V6-03/CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-015",
    "repo": "codegen",
    "path": "src/sysml_codegen/analysis/__init__.py",
    "kind": "production",
    "symbol_or_command": "DependencyBacktracker",
    "responsibility_id": "PROD-03..19",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "exact graph/projector owner",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-016",
    "repo": "codegen",
    "path": "src/sysml_codegen/analysis/part_instance_index.py",
    "kind": "production",
    "symbol_or_command": "InstanceOccurrence, PartInstanceIndex, PathStep",
    "responsibility_id": "PROD-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "exact graph/envelope owner",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-017",
    "repo": "codegen",
    "path": "src/sysml_codegen/cli/__init__.py",
    "kind": "production",
    "symbol_or_command": "GrandfatheredSnapshotError, collect_uncovered_params, constraint_lowering_mode",
    "responsibility_id": "API-07/08",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "preserved public CLI over exact routes",
    "replacement_test": "CUT-CLI-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-018",
    "repo": "codegen",
    "path": "src/sysml_codegen/elaboration/elaborate.py",
    "kind": "production",
    "symbol_or_command": "compile_calc_def_exact, evaluate_identified_profile, extract_identified_constraint_facts",
    "responsibility_id": "PROD-16/20/21",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "sole exact elaboration and unsuffixed upstream route",
    "replacement_test": "CUT-CON-01/CUT-COMP-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-019",
    "repo": "codegen",
    "path": "src/sysml_codegen/orchestration/__init__.py",
    "kind": "production",
    "symbol_or_command": "build_output_registry",
    "responsibility_id": "PROD-01/API-01/05/10",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "sole live/offline orchestration",
    "replacement_test": "CUT-API-01/CUT-V6-03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-020",
    "repo": "codegen",
    "path": "src/sysml_codegen/orchestration/snapshot_context.py",
    "kind": "production",
    "symbol_or_command": "build_full_graph_from_snapshot, load_extraction_snapshot",
    "responsibility_id": "PROD-01/API-01/05/10",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "sole live/offline orchestration",
    "replacement_test": "CUT-API-01/CUT-V6-03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-021",
    "repo": "codegen",
    "path": "src/sysml_codegen/resolution/producer_completeness.py",
    "kind": "production",
    "symbol_or_command": "producer_resolution",
    "responsibility_id": "PROD-07",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "exact graph/envelope owner",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-022",
    "repo": "codegen",
    "path": "src/sysml_codegen/snapshot/__init__.py",
    "kind": "production",
    "symbol_or_command": "GrandfatheredSnapshotError, build_full_graph_from_snapshot, constraint_lowering_mode, load_extraction_snapshot, serialize_extraction_snapshot",
    "responsibility_id": "PROD-12/API-13",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "strict v6 envelope/capture",
    "replacement_test": "CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-023",
    "repo": "codegen",
    "path": "src/sysml_codegen/snapshot/capture.py",
    "kind": "production",
    "symbol_or_command": "constraint_lowering_mode, serialize_extraction_snapshot",
    "responsibility_id": "PROD-12/API-13",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "strict v6 envelope/capture",
    "replacement_test": "CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-024",
    "repo": "codegen",
    "path": "src/sysml_codegen/snapshot/graph_rebuild.py",
    "kind": "production",
    "symbol_or_command": "DependencyBacktracker, _rescue_self_named_bindings, build_computation_graph, build_output_registry, load_extraction_snapshot, supplied_values",
    "responsibility_id": "PROD-12",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "exact graph/envelope owner",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-025",
    "repo": "codegen",
    "path": "src/sysml_codegen/snapshot/loader.py",
    "kind": "production",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "PROD-12",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "exact graph/envelope owner",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-026",
    "repo": "codegen",
    "path": "src/sysml_codegen/snapshot/serializer.py",
    "kind": "production",
    "symbol_or_command": "InstanceOccurrence, constraint_lowering_mode",
    "responsibility_id": "PROD-12",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "exact graph/envelope owner",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-027",
    "repo": "codegen",
    "path": "tests/conformance/conftest.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03.06",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03.06",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-028",
    "repo": "codegen",
    "path": "tests/conformance/test_agg_localterm_default.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-029",
    "repo": "codegen",
    "path": "tests/conformance/test_aggregation_scoping.py",
    "kind": "test",
    "symbol_or_command": "build_output_registry",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-030",
    "repo": "codegen",
    "path": "tests/conformance/test_alias_agg_probe_generation.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-031",
    "repo": "codegen",
    "path": "tests/conformance/test_constraint_occurrence_demand_acceptance.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-032",
    "repo": "codegen",
    "path": "tests/conformance/test_constraint_snapshot_identity.py",
    "kind": "test",
    "symbol_or_command": "serialize_extraction_snapshot",
    "responsibility_id": "TEST-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03",
    "replacement_test": "CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-033",
    "repo": "codegen",
    "path": "tests/conformance/test_crosspart_rollup_twolevel.py",
    "kind": "test",
    "symbol_or_command": "producer_completeness, producer_resolution",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-034",
    "repo": "codegen",
    "path": "tests/conformance/test_deep_cross_scope_probe.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot, collect_uncovered_params",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-035",
    "repo": "codegen",
    "path": "tests/conformance/test_elaboration_dual_run.py",
    "kind": "test",
    "symbol_or_command": "build_elaborated_pipeline",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-036",
    "repo": "codegen",
    "path": "tests/conformance/test_elaboration_model_validation.py",
    "kind": "test",
    "symbol_or_command": "build_elaborated_pipeline",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-037",
    "repo": "codegen",
    "path": "tests/conformance/test_elaboration_payload_identity.py",
    "kind": "test",
    "symbol_or_command": "compile_calc_def_exact, evaluate_identified_profile",
    "responsibility_id": "TEST-01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-01",
    "replacement_test": "CUT-PAY-01/CUT-CON-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-038",
    "repo": "codegen",
    "path": "tests/conformance/test_entry_point_classifier.py",
    "kind": "test",
    "symbol_or_command": "build_computation_graph, build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-039",
    "repo": "codegen",
    "path": "tests/conformance/test_expression_compiler.py",
    "kind": "test",
    "symbol_or_command": "compile_calc_def_exact",
    "responsibility_id": "TEST-05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-05",
    "replacement_test": "CUT-COMP-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-040",
    "repo": "codegen",
    "path": "tests/conformance/test_extraction_snapshots.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03",
    "replacement_test": "CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-041",
    "repo": "codegen",
    "path": "tests/conformance/test_factory_purity.py",
    "kind": "test",
    "symbol_or_command": "DependencyBacktracker, build_computation_graph, build_output_registry, load_extraction_snapshot, producer_resolution",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-042",
    "repo": "codegen",
    "path": "tests/conformance/test_fusion_tea_snapshot.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot, collect_uncovered_params",
    "responsibility_id": "TEST-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03",
    "replacement_test": "CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-043",
    "repo": "codegen",
    "path": "tests/conformance/test_gen_json_templates.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-044",
    "repo": "codegen",
    "path": "tests/conformance/test_gen_module_wrappers.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-045",
    "repo": "codegen",
    "path": "tests/conformance/test_gen_pipeline_yaml.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-046",
    "repo": "codegen",
    "path": "tests/conformance/test_gen_registry.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-047",
    "repo": "codegen",
    "path": "tests/conformance/test_gen_schemas.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-048",
    "repo": "codegen",
    "path": "tests/conformance/test_gen_stencils.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-049",
    "repo": "codegen",
    "path": "tests/conformance/test_generation_boundary.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-050",
    "repo": "codegen",
    "path": "tests/conformance/test_grandfather_carveout.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-051",
    "repo": "codegen",
    "path": "tests/conformance/test_graph_assembly.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-052",
    "repo": "codegen",
    "path": "tests/conformance/test_ife_plant.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot, load_extraction_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-053",
    "repo": "codegen",
    "path": "tests/conformance/test_legacy_snapshot_closure.py",
    "kind": "test",
    "symbol_or_command": "GrandfatheredSnapshotError, build_full_graph_from_snapshot, constraint_lowering_mode",
    "responsibility_id": "TEST-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "independent replacement named by TEST-03",
    "replacement_test": "CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-054",
    "repo": "codegen",
    "path": "tests/conformance/test_matcher_reclassification.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-055",
    "repo": "codegen",
    "path": "tests/conformance/test_parameter_group_deriver.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-056",
    "repo": "codegen",
    "path": "tests/conformance/test_pipeline_e2e.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-057",
    "repo": "codegen",
    "path": "tests/conformance/test_pipeline_module_expansion.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-058",
    "repo": "codegen",
    "path": "tests/conformance/test_plant_value_shapes.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot, collect_uncovered_params",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-059",
    "repo": "codegen",
    "path": "tests/conformance/test_plant_values.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot, collect_uncovered_params",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-060",
    "repo": "codegen",
    "path": "tests/conformance/test_res08_consumer_scope_paths.py",
    "kind": "test",
    "symbol_or_command": "DependencyBacktracker, build_output_registry, load_extraction_snapshot, producer_resolution",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-061",
    "repo": "codegen",
    "path": "tests/conformance/test_return_style_extraction.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-062",
    "repo": "codegen",
    "path": "tests/conformance/test_self_named_binding_trap.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-063",
    "repo": "codegen",
    "path": "tests/conformance/test_snapshot_constraint_parity.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03",
    "replacement_test": "CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-064",
    "repo": "codegen",
    "path": "tests/conformance/test_snapshot_contract.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot, load_extraction_snapshot",
    "responsibility_id": "TEST-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03",
    "replacement_test": "CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-065",
    "repo": "codegen",
    "path": "tests/conformance/test_source_identity_routes.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-066",
    "repo": "codegen",
    "path": "tests/conformance/test_type_indexing.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-067",
    "repo": "codegen",
    "path": "tests/conformance/test_type_mapping_consolidation.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-068",
    "repo": "codegen",
    "path": "tests/conformance/test_whole_tree_portability.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-069",
    "repo": "codegen",
    "path": "tests/conformance/test_wi014_toy.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot, build_output_registry, load_extraction_snapshot",
    "responsibility_id": "TEST-01.01",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-01.01",
    "replacement_test": "CUT-F26-01/CUT-V6-03/CUT-ABS-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-070",
    "repo": "codegen",
    "path": "tests/conformance/test_written_qualifier_anchoring.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-071",
    "repo": "codegen",
    "path": "tests/fixtures/agg_literal_probe/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-072",
    "repo": "codegen",
    "path": "tests/fixtures/agg_localterm_probe/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-073",
    "repo": "codegen",
    "path": "tests/fixtures/alias_agg_probe/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-074",
    "repo": "codegen",
    "path": "tests/fixtures/attr_expr_probe/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-075",
    "repo": "codegen",
    "path": "tests/fixtures/catf_mfe_model/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-076",
    "repo": "codegen",
    "path": "tests/fixtures/chain_override_probe/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-077",
    "repo": "codegen",
    "path": "tests/fixtures/chain_spike_model/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-078",
    "repo": "codegen",
    "path": "tests/fixtures/constraint_inline/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-079",
    "repo": "codegen",
    "path": "tests/fixtures/constraint_multi_instance/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-080",
    "repo": "codegen",
    "path": "tests/fixtures/constraint_non_numerical/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-081",
    "repo": "codegen",
    "path": "tests/fixtures/crosspart_rollup_twolevel/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-082",
    "repo": "codegen",
    "path": "tests/fixtures/d38_caret/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-083",
    "repo": "codegen",
    "path": "tests/fixtures/deep_cross_scope_probe/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-084",
    "repo": "codegen",
    "path": "tests/fixtures/expression_binding_probe/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-085",
    "repo": "codegen",
    "path": "tests/fixtures/fusion_tea/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-086",
    "repo": "codegen",
    "path": "tests/fixtures/gate_a_package_owner/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-087",
    "repo": "codegen",
    "path": "tests/fixtures/gate_a/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-088",
    "repo": "codegen",
    "path": "tests/fixtures/ife_plant/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-089",
    "repo": "codegen",
    "path": "tests/fixtures/invocation_binding_probe/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-090",
    "repo": "codegen",
    "path": "tests/fixtures/issue22_model/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-091",
    "repo": "codegen",
    "path": "tests/fixtures/modeled_default_fidelity/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-092",
    "repo": "codegen",
    "path": "tests/fixtures/nested_occurrence_override_probe/PROVENANCE.md",
    "kind": "fixture",
    "symbol_or_command": "supplied_values",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent authored fixture/provenance",
    "replacement_test": "CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-093",
    "repo": "codegen",
    "path": "tests/fixtures/plant_value_shapes/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-094",
    "repo": "codegen",
    "path": "tests/fixtures/plant_values/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-095",
    "repo": "codegen",
    "path": "tests/fixtures/quoted_owner_formula/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-096",
    "repo": "codegen",
    "path": "tests/fixtures/return_styles/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-097",
    "repo": "codegen",
    "path": "tests/fixtures/retype_model/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-098",
    "repo": "codegen",
    "path": "tests/fixtures/sample_model/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-099",
    "repo": "codegen",
    "path": "tests/fixtures/self_named_binding_trap/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-100",
    "repo": "codegen",
    "path": "tests/fixtures/self_named_rescue/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-101",
    "repo": "codegen",
    "path": "tests/fixtures/shadowed_reference/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-102",
    "repo": "codegen",
    "path": "tests/fixtures/shared_producer/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-103",
    "repo": "codegen",
    "path": "tests/fixtures/shared_producer/PROVENANCE.md",
    "kind": "fixture",
    "symbol_or_command": "producer_resolution",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent authored fixture/provenance",
    "replacement_test": "CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-104",
    "repo": "codegen",
    "path": "tests/fixtures/sibling_channel_ambiguity/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-105",
    "repo": "codegen",
    "path": "tests/fixtures/solar_battery_model/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-106",
    "repo": "codegen",
    "path": "tests/fixtures/spec_chain_channel/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-107",
    "repo": "codegen",
    "path": "tests/fixtures/spec_chain_twolevel/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "delete",
    "final_owner": "typed refusal with no snapshot",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-108",
    "repo": "codegen",
    "path": "tests/fixtures/two_same_leaf_producers/README.md",
    "kind": "fixture",
    "symbol_or_command": "producer_completeness",
    "responsibility_id": "TEST-04",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent authored fixture/provenance",
    "replacement_test": "CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-109",
    "repo": "codegen",
    "path": "tests/fixtures/unresolvable_attr_probe/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-110",
    "repo": "codegen",
    "path": "tests/fixtures/wi014_toy/extraction_snapshot.json",
    "kind": "fixture",
    "symbol_or_command": "constraint_lowering_mode",
    "responsibility_id": "B37-01..37",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "accepted v6 envelope",
    "replacement_test": "CUT-CORP-01/CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-111",
    "repo": "codegen",
    "path": "tests/integration/test_full_pipeline.py",
    "kind": "test",
    "symbol_or_command": "DependencyBacktracker, build_computation_graph",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-112",
    "repo": "codegen",
    "path": "tests/integration/test_parallel_validation.py",
    "kind": "test",
    "symbol_or_command": "build_output_registry",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-113",
    "repo": "codegen",
    "path": "tests/unit/test_computed_attribute_extraction.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-114",
    "repo": "codegen",
    "path": "tests/unit/test_constraint_graph_extension.py",
    "kind": "test",
    "symbol_or_command": "collect_uncovered_params",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-115",
    "repo": "codegen",
    "path": "tests/unit/test_constraint_usage_preparation.py",
    "kind": "test",
    "symbol_or_command": "InstanceOccurrence, PathStep, supplied_values",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-116",
    "repo": "codegen",
    "path": "tests/unit/test_design_overrides_threaded.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-117",
    "repo": "codegen",
    "path": "tests/unit/test_exit_point_aliases.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-118",
    "repo": "codegen",
    "path": "tests/unit/test_expression_compiler.py",
    "kind": "test",
    "symbol_or_command": "compile_calc_def_exact",
    "responsibility_id": "TEST-05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-05",
    "replacement_test": "CUT-COMP-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-119",
    "repo": "codegen",
    "path": "tests/unit/test_logical_demand_resolution.py",
    "kind": "test",
    "symbol_or_command": "supplied_values",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-120",
    "repo": "codegen",
    "path": "tests/unit/test_part_instance_index.py",
    "kind": "test",
    "symbol_or_command": "InstanceOccurrence, PartInstanceIndex, PathStep",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-121",
    "repo": "codegen",
    "path": "tests/unit/test_silent_failure_family2_family3_fires.py",
    "kind": "test",
    "symbol_or_command": "build_output_registry",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-122",
    "repo": "codegen",
    "path": "tests/unit/test_snapshot_envelope_gate.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03",
    "replacement_test": "CUT-V6-01/02/03",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-123",
    "repo": "codegen",
    "path": "tests/unit/test_source_referent_shape_gate.py",
    "kind": "test",
    "symbol_or_command": "load_extraction_snapshot",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-124",
    "repo": "codegen",
    "path": "tests/unit/test_supplied_values.py",
    "kind": "test",
    "symbol_or_command": "supplied_values",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  },
  {
    "id": "INV-RES-CG-125",
    "repo": "codegen",
    "path": "tests/unit/test_uncovered_params.py",
    "kind": "test",
    "symbol_or_command": "build_full_graph_from_snapshot, collect_uncovered_params",
    "responsibility_id": "TEST-03/04/05",
    "status": "existing",
    "current_owner": "current executable residue surface",
    "disposition": "migrate",
    "final_owner": "independent replacement named by TEST-03/04/05",
    "replacement_test": "CUT-ABS-01/CUT-PROJ-01",
    "residue_gate": "NR-01..09/13"
  }
  ]
}
-->

## Replacement Test Catalog

These IDs are exact implementation obligations. Expected values come from the SysML model, accepted
contract, hand calculation, format schema, or explicit graph fixture named here. None may execute the
legacy front end, copy its output at runtime, or inspect a compatibility field.

| ID | Exact final test | Independent oracle |
|---|---|---|
| `CUT-API-01` | `tests/conformance/test_cutover_public_api.py::test_public_surface_and_builder_created_context_are_closed` | This census's exact signatures/export table. |
| `CUT-API-02` | `tests/conformance/test_cutover_public_api.py::test_context_has_one_defensive_graph_view_and_no_public_constructor` | Canonical immutable bytes/selection/receipt lifetime in design D1. |
| `CUT-REC-01` | `tests/conformance/test_cutover_projection_receipt.py::test_each_bound_field_and_mutation_is_verified_at_generation_boundaries` | Independently recomputed instance, selection, projector, and full computation digests. |
| `CUT-PROMO-01` | `tests/unit/test_check_cutover_candidate.py` | Canonical singular record; record-self canonicalization; schema-declared evidence templates, sentinel pointers, deterministic materialization/reversal; full inventories; command/result/environment binding; exact annotated tag objects; and phase input rejection. |
| `CUT-PROMO-02` | `tests/integration/test_cutover_candidate_promotion.py` | Two temporary authoritative bare origins prove local prepare without public branch advance, remote branch/product-tag CAS, observed/returned OIDs, second-origin compensation, rollback hard block, authorized recovery, crash recovery, post-publication tag verification, and release refusal/acceptance. |
| `CUT-PROMO-03` | `tests/conformance/test_cutover_candidate_workflows.py` | Both repositories' protected branch/tag/release workflow callers use only `scripts/check_cutover_candidate.py` and the required peer checkout/state. |
| `CUT-CENSUS-01` | `tests/unit/test_check_cutover_census.py` | Deterministic two-worktree generation, uncensused-marker refusal, sorted rows, stable IDs, and census/inventory exact equality. |
| `CUT-RESIDUE-01` | `tests/unit/test_check_cutover_residue.py` | Encoded vocabulary cannot self-match; AST/non-Python residues are distinguished from declared transitional inventory and absent final state. |
| `CUT-CLI-01` | `tests/unit/test_cli_generation.py::test_cutover_cli_flag_and_exit_contract` | Existing argparse contract plus spec R3. |
| `CUT-V6-01` | `tests/conformance/test_snapshot_v6_envelope.py::test_complete_envelope_round_trip_and_exact_shape` | V6 field schema in design D5. |
| `CUT-V6-02` | `tests/conformance/test_snapshot_v6_envelope.py::test_tamper_skew_order_and_failure_types` | Hand-mutated bytes at each ordered validation layer. |
| `CUT-V6-03` | `tests/conformance/test_snapshot_v6_routes.py::test_live_in_place_and_relocated_semantics_match` | One live graph fingerprint and off-default model mutation. |
| `CUT-CAP-01` | `tests/conformance/test_snapshot_v6_capture.py::test_capture_refusal_is_atomic_and_writes_nothing` | Named authored diagnostic plus sentinel destination. |
| `CUT-SRC-01` | `tests/conformance/test_source_admission_routes.py` plus `tests/unit/test_source_admission.py` | Exact staged bytes/document-set/root policy in design D3/D6. |
| `CUT-OCC-01` | `tests/conformance/test_elaboration_occurrence.py::test_exact_parent_slot_index_and_effective_child` | Authored containment/specialization structure, not rendered paths. |
| `CUT-BIND-01` | `tests/conformance/test_elaboration_contract_matrix.py` D-5/SRC-01 rows | Inherited binding-shape contract by path. |
| `CUT-AGG-01` | `tests/conformance/test_elaboration_aggregations.py::test_typed_fold_edges_and_plural_scope` | Authored aggregation AST and concrete occurrence membership. |
| `CUT-SEL-01` | `tests/conformance/test_cutover_target_selection.py::test_exact_edge_closure_preserves_targets_and_constraint_roots` | Hand-enumerated graph nodes/edges. |
| `CUT-RES-01` | `tests/conformance/test_elaboration_public_mutation.py::test_each_source_reaches_every_and_only_bound_consumers` | Authored bindings plus negative unaffected set. |
| `CUT-C19-01` | `tests/conformance/test_cutover_c19.py::test_nested_override_80_reaches_calc_and_constraint_on_all_routes` | Literal `80.0` in maintained C19 SysML and exact consumer IDs. |
| `CUT-REG-01` | `tests/conformance/test_elaboration_projection.py::test_source_cardinality_aliases_and_entry_groups` | Exact source nodes and hand-declared consumer sets. |
| `CUT-PROJ-01` | `tests/conformance/test_elaboration_projection_one_way.py::test_projection_never_reconstructs_identity` | Static import boundary plus typed edge fixture. |
| `CUT-COMP-01` | `tests/conformance/test_exact_compiler_core.py::test_all_call_shapes_use_one_id_keyed_compiler_core` | Hand-authored expression IR and expected Python expressions. |
| `CUT-CON-01` | `tests/conformance/test_exact_constraint_route.py::test_identified_fact_profile_and_projected_constraint_agree` | Exact declaration/formal IDs and profile decisions. |
| `CUT-PAY-01` | `tests/conformance/test_elaboration_payload_identity.py::test_payload_maps_are_id_keyed_and_round_trip` | Distinct same-name declaration IDs. |
| `CUT-F26-01` | `tests/conformance/test_wi014_toy.py::test_f26_literal_public_projection_oracle` | Literal group, four keys, alias tuple, and constraint ID recorded below; no old builder. |
| `CUT-CORP-01` | `tests/conformance/test_cutover_manifest.py::test_manifest_has_exact_37_paths_and_allowed_outcomes` | Accepted Item-5 37-row ledger plus R7. |
| `CUT-ABS-01` | `tests/conformance/test_cutover_no_legacy_residue.py::test_closed_census_has_no_runtime_residue` | Filename/symbol/export gates NR-01 through NR-08. |
| `CUT-FT-01` | `tests/conformance/test_fusion_tea_cutover.py::test_15_bare_renamed_bindings_and_generated_names` | Exact rename table in design D11. |
| `CUT-C25-01` | `tests/conformance/test_fusion_tea_cutover.py::test_c25_availability_one_source_exact_two_consumers` | C25 source, 0.90 override, and two named consumers. |
| `CUT-C2-01` | `tests/conformance/test_fusion_tea_cutover.py::test_c2_thermal_efficiency_one_source_exact_two_consumers` | C2 source, 0.43 override, and two named consumers. |
| `CUT-ARITH-01` | `tests/conformance/test_compile_calc_def_golden.py::test_fusion_tea_arithmetic_goldens_after_formal_rename` | Hand-authored formula/result goldens, including unchanged `lcoe`, `gamma`, and `f_recirc` controls. |
| `CUT-TEAX-01` | `tests/execution/test_fusion_tea_item7_real_teax.py::test_live_and_relocated_packages_verify_and_execute` | Public real TEAx APIs and hand-derived LCOE `270.1211779380445`. |
| `CUT-SCALE-01` | `tests/execution/test_fusion_tea_item7_budget.py::test_three_measured_runs_meet_budget_and_are_stable` | R10 thresholds and exact repeated counts. |

## R3 Public Surface Census

Caller-set IDs used in the table are expanded immediately below it. “Same alias” means object
identity with the orchestration-owned symbol, not a wrapper.

| ID | Current repository/import and surface | Current signature/flags → return/errors | Current callers/re-exports | Final disposition and surface | Final return/errors; compatibility | Migration owner | Acceptance |
|---|---|---|---|---|---|---|---|
| `API-01` | codegen `sysml_codegen.orchestration.pipeline_builder.build_pipeline_context` | `(model_paths: list[Path], targets: list[str] | None=None, include_all: bool=True, design_path_filter: str="", lower_constraints_enabled: bool=True) -> PipelineContext`; `SysMLParsingError`, `CodeGenerationError`, leaked internal errors | `CALL-LIVE`; orchestration export only | **MIGRATE** in place to `(model_paths, targets=None, include_all=True, design_path_filter="")`; staged admission → exact elaborate → canonical selection → private context factory | Builder-created context; named live/admission/elaboration/projection errors. Delete lowering flag with no alias. | `orchestration/pipeline_builder.py` | `CUT-API-01`, `CUT-SRC-01`, `CUT-SEL-01` |
| `API-02` | codegen `sysml_codegen.orchestration.pipeline_context.PipelineContext` | Wide mutable dataclass with extractor, calc/usage/design maps, group deriver, backtracker/result, graph, compilation, computed/aggregation/alias/registry/constraint/occurrence/lowering fields | `CALL-CONTEXT`; orchestration plus two current type/error alias modules | **MIGRATE** to frozen/slotted builder-created type. Public `__new__`/`__init__` always raise; no public factory. Private state is canonical instance bytes, canonical selection, immutable receipt. | Sole public data property `.computation_graph` redecodes/reprojects/verifies and returns a fresh deep graph. No `.instance_graph`, selection, receipt, mutation, pickle, replace, legacy kwargs, or arbitrary pair. | `orchestration/pipeline_context.py` | `CUT-API-01/02`, `CUT-REC-01` |
| `API-03` | codegen internal `orchestration.elaborated_pipeline.build_elaborated_pipeline` | `(model_paths: list[Path]) -> ComputationGraph`; live load/exact errors | `scripts/run_elaboration_corpus.py`, dual-run and exact-boundary tests | **DELETE**. Private `load_and_elaborate(...) -> InstanceGraph` is the shared implementation under API-01/capture, not another public builder. | No compatibility import. | API-01 owner | `CUT-ABS-01`, `CUT-V6-03` |
| `API-04` | codegen `sysml_codegen.snapshot.capture_snapshot` | `(model_paths: list[Path], output_path: Path, design_path_filter: str="") -> Path`; live errors and `OSError`; direct non-atomic overwrite | `CALL-CAPTURE`; snapshot re-export | **MIGRATE** same signature to strict full-graph v6 atomic capture | Same `Path`; named live errors, `Snapshot*` self-validation errors, `OSError`; existing destination unchanged on failure. | `snapshot/capture.py` | `CUT-CAP-01`, `CUT-V6-01` |
| `API-05` | codegen `orchestration.snapshot_context.build_pipeline_context_from_snapshot` | `(snapshot_path: Path) -> PipelineContext`; v5 load/rebuild errors | CLI and `CALL-SNAPSHOT`; orchestration export only | **MIGRATE** to `(snapshot_path: Path, targets=None, include_all=True, *, source_roots: Sequence[Path] | None=None)`; ordered v6 validation/freshness → canonical selection → same private context factory | Reject string/bytes/non-Path member/set/generator/mapping with `TypeError`; empty sequence is `SnapshotStaleSourceError`; `None` is unverified. Same receipt/errors as API-01. | `orchestration/snapshot_context.py` | `CUT-V6-03`, `CUT-SEL-01`, `CUT-REC-01`, `CUT-SRC-01` |
| `API-06` | codegen snapshot low-level exports: `load_extraction_snapshot`, `serialize_extraction_snapshot`, `snapshot_to_json`, `build_classifier_inputs_from_snapshot`, `build_full_graph_from_snapshot`, `assert_snapshot_certifiable` | v5 extraction DTOs/tuples/JSON; `SnapshotFormatError`, runtime/profile errors | `CALL-SNAPSHOT`; `sysml_codegen.snapshot` exports | **DELETE** all named surfaces. **MIGRATE capability** to `snapshot.load_snapshot(path: Path, *, source_roots: Sequence[Path] | None=None) -> InstanceGraph`; capture is sole public encoder; API-05 is sole public projector. | Same exact root-type rules; ordered v6 `Snapshot*`; no extraction DTO, graph rebuild, cert helper, or alias. Every graph `source_file` must equal one manifest referent. | `snapshot/envelope.py`; API-04/05 owners | `CUT-V6-01/02/03`, `CUT-SRC-01`, `CUT-ABS-01` |
| `API-07` | codegen CLI `generate` | exactly one `--models/-m` or `--from-snapshot`; required `--output/-o`; package/schema/pipeline/overwrite/preserve/smart/verbose/filter; filter+snapshot error; 0/1 | Console entry point and CLI tests | **MIGRATE** implementation only; preserve every current flag, default, exclusion, and exit code. Python-only target/include remain API-01/05 capabilities; no invented CLI flags. | Named failure logged once, 1, and no output clearing/writing; success 0. | `cli/__init__.py` | `CUT-CLI-01`, `CUT-V6-03` |
| `API-08` | codegen CLI `snapshot` | required `--models/-m`; optional `--output/-o` default `<models>/extraction_snapshot.json`; filter/verbose; uncaught capture failures today | Console entry point and CLI/capture tests | **MIGRATE** same flags/default/success output. Catch named capture/format/I/O errors and return 1. | Success 0/`Path` log; failure 1, no new/partial artifact, old destination unchanged. | `cli/__init__.py` | `CUT-CLI-01`, `CUT-CAP-01` |
| `API-09` | codegen live errors `CodeGenerationError`, `SysMLParsingError`; snapshot `SnapshotFormatError`, `GrandfatheredSnapshotError` | Exception classes; broad current leakage | generation/orchestration/snapshot re-exports | **RETAIN** live errors; add closed `SourceAdmissionError`/`SourceAdmissionCode`, including `SOURCE_STANDARD_LIBRARY_UNAVAILABLE`; **MIGRATE** snapshot family to `SnapshotFormatError`, `SnapshotIntegrityError`, `SnapshotCompatibilityError`, `SnapshotStaleSourceError`, `SnapshotCertifiabilityError`; **DELETE** grandfather class | Live/capture unavailable/unreadable standard library is typed admission failure. Stored/pinned digest mismatch remains `SnapshotCompatibilityError`. No aliases. | generation/errors.py; `snapshot/source_manifest.py`; `snapshot/envelope.py` | `CUT-API-01`, `CUT-SRC-01`, `CUT-V6-02` |
| `API-10` | `sysml_codegen.orchestration` exports wide context, live errors, builder, registry/helper legacy symbols | Re-export module | Public import callers | **MIGRATE** to only context, API-01, API-05, live exact errors. Delete registry/helper exports. | Same alias identities; importing a deleted symbol fails. | `orchestration/__init__.py` | `CUT-API-01`, `CUT-ABS-01` |
| `API-11` | `sysml_codegen.generation` currently aliases `PipelineContext`, `CodeGenerationError`, `SysMLParsingError`; it does not export a builder | Same objects via initialization | Public type/error import callers | **RETAIN** exactly those three aliases; generation-specific exports remain. Do not add API-01 or API-05. | Object-identical aliases; no wrapper/construction. | `generation/__init__.py` | `CUT-API-01`, NR-06 |
| `API-12` | `sysml_codegen.generation.initialization` currently aliases `PipelineContext`, `CodeGenerationError`, `SysMLParsingError`; it does not export a builder | Three-symbol compatibility module | generation `__init__` and old type/error imports | **RETAIN** exactly those three pure aliases. No logic, builder, factory, or legacy fields. | Object-identical aliases. | `generation/initialization.py` | `CUT-API-01`, NR-06 |
| `API-13` | `sysml_codegen.snapshot` exports v5 constants, modes, errors, loader/rebuilders/serializers/capture | Mixed public surface | Snapshot callers | **MIGRATE** to `SNAPSHOT_FORMAT_VERSION=6`, v6 error family, `capture_snapshot`, `load_snapshot`. API-05 remains orchestration-owned. | No v5 mode constants, cert helper, serializer, rebuild, or grandfather alias. | `snapshot/__init__.py` | `CUT-V6-01`, `CUT-ABS-01` |
| `API-14` | package root `sysml_codegen` | Does not export orchestration/snapshot authority | Package metadata tests | **RETAIN** no new root export. | Importing builders/context from root remains unsupported. | `sysml_codegen/__init__.py` | `CUT-API-01` |

### Explicit caller sets

- `CALL-LIVE` production: `src/sysml_codegen/cli/__init__.py`,
  `src/sysml_codegen/snapshot/capture.py`. Scripts:
  `scripts/_q5_debug.py`, `capture_baseline_yaml.py`, `capture_extraction_snapshots.py`,
  `capture_pipeline_baselines.py`, `run_elaboration_corpus.py`, and the affected probe/spike group in
  `SCR-03`. Tests: all members of `TEST-02`, `TEST-03`, and `TEST-04` below.
- `CALL-CONTEXT` production: `src/sysml_codegen/cli/__init__.py`, generation helpers that accept
  context (`generation/constraint_plan.py`, `generation/pipeline.py`), and the public re-export files
  `orchestration/__init__.py`, `generation/__init__.py`, `generation/initialization.py`. Tests:
  `test_orchestrator.py`, `test_generation_boundary.py`, `test_elaboration_generation_boundary.py`,
  `test_cli_generation.py`, `test_constraint_pipeline_threading.py`, and integration pipeline tests.
  Final package-writing/sealing callers obtain one verified projection lease and verify it again
  before seal; pure graph render helpers remain non-certifying.
- `CALL-CAPTURE`: CLI; `scripts/capture_extraction_snapshots.py`; snapshot contract, portability,
  constraint parity, source identity route, CLI, and corpus tests in `TEST-03`.
- `CALL-SNAPSHOT`: CLI; `scripts/capture_baseline_yaml.py`, `capture_pipeline_baselines.py`; current
  snapshot, generation, Fusion Tea, runtime, and execution files in `TEST-03`/`TEST-04`.

## R6 Production Responsibility Census

| ID | Repository; explicit owner/member(s) | Current responsibility | Disposition and final owner | Caller/export migration and preserved oracle | Replacement / no-residue |
|---|---|---|---|---|---|
| `PROD-01` | codegen `orchestration/pipeline_builder.py` | Legacy semantic front end: extraction, VBR/self rescue, scope repair, registry, backtracking, compilation, graph assembly | **MIGRATE/DELETE body**. File becomes the small API-01 exact orchestrator. All nested legacy helpers disappear. | CALL-LIVE to exact graph; preserve target/include/filter and current generation output where contract permits. | `CUT-API-01`, `CUT-SEL-01`; NR-01/02 |
| `PROD-02` | codegen `orchestration/elaborated_pipeline.py`, `elaboration/diff.py` | Parallel exact builder and exact-vs-legacy comparator | **DELETE** both. Shared private load/elaborate function lives under PROD-01; no diff owner. | F26 literal names/IDs → `CUT-F26-01`; live/in-place/relocated agreement → `CUT-V6-03`; old-route absence → `CUT-ABS-01`. | `CUT-F26-01`, `CUT-V6-03`, `CUT-ABS-01`; NR-01 |
| `PROD-03` | codegen `analysis/part_instance_index.py` and its exports | `PartInstanceIndex`, `PathStep`, legacy `InstanceOccurrence`, rendered-path occurrence query | **DELETE**. Exact `elaboration/occurrence.py` and graph occurrence records own structure. | All constraint/graph callers use exact occurrence/declaration IDs. | `CUT-OCC-01`, `CUT-CON-01`; NR-02 |
| `PROD-04` | codegen VBR/repair helpers nested in `pipeline_builder.py`; `extraction/usage_extractor.py` virtual expansion portions | Virtual-binding rewrite, specialized-chain rewrite, alias expansion, self-named rescue, virtual calc usages | **DELETE**. `elaboration/elaborate.py` exact writer and binding resolution are sole owners. Prune only legacy portions of usage extraction after exact callers move. | D-5/SRC-01 outcomes and F19 replace repair behavior. | `CUT-BIND-01`, `CUT-FT-01`; NR-02 |
| `PROD-05` | codegen `analysis/parameter_groups.py`, legacy aggregation/hierarchy helpers in `pipeline_builder.py`, legacy-only portions of `extraction/hierarchy_resolver.py` and `computed_attribute_extractor.py` | Name/path scope re-derivation, aggregation grouping, group value backfill | **DELETE legacy semantics**. Exact occurrence expansion and typed expression edges stay in `elaboration/elaborate.py`; rendering stays in `project.py`. | Preserve authored aggregation fold/cardinality and generated parameter groups from exact sources. | `CUT-AGG-01`, `CUT-REG-01`; NR-02 |
| `PROD-06` | codegen `analysis/dependency_backtracker.py`, `signature_extractor.py`, `phantom_detector.py` | Semantic edge-discovery ladder, reverse channel parsing, pruning support, legacy signatures/phantoms | **DELETE** as legacy owner. Exact target closure/topological ordering follows typed edges in `elaboration/project.py`. Retain no helper that accepts rendered channels as identity. | Target/include behavior and constraint roots preserved. | `CUT-SEL-01`; NR-03 |
| `PROD-07` | codegen `resolution/producer_resolution.py`, `producer_completeness.py` | 21-key-form table, scope climb, completeness over reconstructed candidates | **DELETE**. Exact elaboration owns binding; graph validation owns completeness. | Every-and-only mutation plus diagnostic matrix. | `CUT-RES-01`, `CUT-BIND-01`; NR-03 |
| `PROD-08` | codegen `resolution/supplied_values.py` | Supplied-value materializer, def-context remap, C19 tripwire | **DELETE**. Effective occurrence values are materialized during exact elaboration. | C19 literal 80.0 reaches exact calc and constraint ports. | `CUT-C19-01`; NR-03 |
| `PROD-09` | codegen `core/output_registry.py`, `orchestration/output_registry_builder.py`, exports from `core/__init__.py`/`orchestration/__init__.py` | `OutputRegistry` namespaces, aliases, reverse lookup, phased builder | **DELETE**. Exact graph owns nodes/edges; projection owns public aliases and entry groups. | Source cardinality, alias, entry-group behavior remains independently tested. | `CUT-REG-01`; NR-03 |
| `PROD-10` | codegen `resolution/graph_builder.py` | Legacy `build_computation_graph`, constraint extension, uncovered-parameter inspection, group backfill | **DELETE**. `elaboration/project.py` is the only graph projector; graph validation makes “uncovered” a boundary failure. | Generated module/EP/catalog semantics from exact graph. | `CUT-PROJ-01`, `CUT-REG-01`; NR-03 |
| `PROD-11` | codegen `resolution/models.py` | Generation `ComputationGraph` and DTO seam | **RETAIN** as non-authoritative downstream data. | May be imported by projection and generation only; cannot import orchestration, snapshot, extraction, or legacy resolution owners. | `CUT-PROJ-01`; NR-07 |
| `PROD-12` | codegen `snapshot/serializer.py`, `loader.py`, `graph_rebuild.py`; v5 portions of `snapshot/capture.py`, `snapshot/__init__.py`, `orchestration/snapshot_context.py` | V5 extraction DTO serialization, load, semantic rebuild, grandfather mode | **DELETE/REPLACE** with `snapshot/envelope.py`, `source_manifest.py`, strict capture, and v6 snapshot context. | API-04/05/06/13 migrations; relocation and failure order preserved by v6 contract. | `CUT-V6-01/02/03`, `CUT-CAP-01`; NR-04 |
| `PROD-13` | codegen `snapshot/instance_graph.py` | Internal exact graph v2 codec | **RETAIN/MIGRATE** under v6 envelope. Harden exact-key and duplicate validation; keep one inner graph digest. | Called only by envelope; never public alternative capture/load authority. | `CUT-V6-01/02`; NR-07 |
| `PROD-14` | codegen `analysis/source_referent.py`; new `snapshot/source_manifest.py` | Lexical root-N mapping today; no parse/hash binding | **MIGRATE** to sole staged admission owner. Preserve ordered roots/overlaps/duplicates/root symlinks/filter paths/`.sysml`/`.kerml`/external roots. Add `SysideStandardLibraryDigestAdapter`, race/document-set/physical/case/NFC rules, and typed `SOURCE_STANDARD_LIBRARY_UNAVAILABLE`. Delete old import path. | Live/capture/freshness use one immutable admission; SysIDE parses staged hashed bytes. Standard-library mismatch offline remains `SnapshotCompatibilityError`. | `CUT-SRC-01`, `CUT-V6-02/03`; NR-02 |
| `PROD-15` | codegen `analysis/constraint_lowering.py` | Legacy constraint preparation/lowering plus two still-useful helpers | **DELETE**. Move `resolve_modeled_default` to `elaboration/value_defaults.py`; move `mint_constraint_id` to `generation/constraint_catalog.py`. | Exact elaboration/project imports neutral owners; no legacy lowering import. | `CUT-CON-01`, `CUT-PROJ-01`; NR-03 |
| `PROD-16` | codegen `elaboration/{identity,occurrence,graph,elaborate,diagnostics,display}.py` | Certified exact IDs, occurrences, payloads, diagnostics, strict graph | **RETAIN** as sole semantics. | Must not import PROD-01 legacy helpers or PROD-03–10/12 old owners. | Item-6 exact suites plus `CUT-OCC-01`, `CUT-CON-01`; NR-07 |
| `PROD-17` | codegen `elaboration/project.py` | Certified one-way exact projection; currently imports legacy constraint ID helper | **MIGRATE/RETAIN**; add target closure, move helper import per PROD-15. | Sole producer of generation `ComputationGraph`. | `CUT-SEL-01`, `CUT-PROJ-01`; NR-07 |
| `PROD-18` | codegen `extraction/expression_compiler.py`, exact callers in `elaboration/elaborate.py` | Item-6 dual 3: `compile_calc_def_exact` beside name-keyed `compile_calc_def`, parallel AST walk/coexistence checks | **MIGRATE** exact implementation to the single `compile_calc_def`; it accepts ID-keyed IR/payload. Delete parallel name-keyed walk, `_exact` public/internal symbol, and equality assertion. Display-name adapters may run after compilation only. | All exact and generation callers use one core; hand-authored compiler goldens remain. | `CUT-COMP-01`; NR-05 |
| `PROD-19` | codegen `extraction/data_models.py`, `expression_compiler.py`, `elaboration/elaborate.py`, v5 serializer | Item-6 dual 4: name-keyed calc maps plus ID sidecars omitted from v5 | **MIGRATE** to one declaration-ID-keyed payload. Names are metadata on the record. Delete sidecar fields and v5 exclusions. | Exact codec round-trip preserves IDs; projection renders names once. | `CUT-PAY-01`; NR-05 |
| `PROD-20` | agentic `src/agentic_mbse/sysml/constraint_extraction.py`, `src/agentic_mbse/sysml/__init__.py`; codegen `elaboration/elaborate.py` | Item-6 dual 1: unsuffixed neutral extraction plus transitional identified extraction/export | **MIGRATE** exact implementation to sole `extract_constraint_facts(model) -> IdentifiedConstraintFacts`. Delete `extract_identified_constraint_facts` and its export. Neutral `.facts` data remains inside the exact product, not a second pass. | Codegen, validation levels 4/6, and extraction tests consume the same exact batch. | `CUT-CON-01`; NR-05/08 |
| `PROD-21` | agentic `src/agentic_mbse/sysml/executable_profile.py` `__all__`; validation `level4_constraints.py`, `level6_architecture.py`; codegen `elaboration/elaborate.py`, `analysis/constraint_lowering.py` | Item-6 dual 2: QN `_evaluate_usage`/`evaluate_profile(ConstraintFacts)` beside exact `evaluate_identified_profile` | **MIGRATE** exact implementation to sole `evaluate_profile(IdentifiedConstraintFacts) -> IdentifiedProfileResult`. Delete `_evaluate_usage`, QN definition map, `evaluate_identified_profile`, its export, and all QN result types if unreferenced. `preflight` accepts an already-decided exact result. | Levels 4/6 consume exact `item.decision`. Any formatter has a distinct `format_*` name, exact-result input, and text-only output; it cannot associate. | `CUT-CON-01`; NR-05/08 |
| `PROD-22` | agentic `src/agentic_mbse/sysml/expression_ir.py`, `constraint_facts.py`, `executable_profile.py`; codegen `_upstream_pins.py` | Certified typed IR, fact/profile versions, deny-by-default behavior | **RETAIN** exact owners and pins. | V6 authority markers exact-match these versions before decode. | `CUT-V6-02`, upstream pin tests; NR-08 |
| `PROD-23` | codegen `generation/*`, `contracts/*`, templates, CLI package writer | Generation and sealing from mutable `ComputationGraph` | **MIGRATE certifying boundaries** to verified projection lease; verify full receipt at entry and before seal. Pure render helpers accept the leased graph but cannot write/seal. Log count comes from that graph. | No generation module imports extraction/snapshot/legacy owners or reads private context state; naked graphs cannot enter a certifying writer. | `CUT-API-02`, `CUT-REC-01`; NR-07 |
| `PROD-24` | codegen Fusion Tea SysML members listed in `FIX-01` | Maintained customer-scale model with 15 D-5 violations | **MIGRATE in place** exactly; no sibling fixture and no arithmetic/source/default changes. | Formal-derived generated inputs change; public source keys/module/schema names stay as design table. | `CUT-FT-01`, `CUT-C25-01`, `CUT-C2-01`, `CUT-TEAX-01` |

## Export and Caller/File Migration Details

### `FIX-01` — exact Fusion Tea edits

- `tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml`: seven `lcoe_calc`, two
  `recirc_calc`, one `viability` occurrence bindings.
- `tests/fixtures/fusion_tea/designs/hif_ife/hif_plant.sysml`: one reactor-cost and two COE bindings.
- `tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml`: two driver-cost bindings.
- `tests/fixtures/fusion_tea/library/analyses/ife_lcoe.sysml`: rename seven formals and all matching
  equation identifiers.
- `tests/fixtures/fusion_tea/library/analyses/fusion_cycle.sysml`: rename two calculation formals and
  one constraint formal plus matching expression identifiers.
- `tests/fixtures/fusion_tea/library/analyses/hif_economics.sysml`: rename five formals and matching
  expression identifiers.
- `tests/fixtures/fusion_tea/extraction_snapshot.json`: delete v5; add v6 only in the accepted batch.

Generated/caller changes are exact: seven `IFE_LCOEInputs` fields, two
`Recirculating_Power_FractionInputs` fields, one viability predicate input, one
`Meier_Reactor_CostInputs` field, two `Meier_COEInputs` fields, and two
`Meier_HIF_Driver_CostInputs` fields gain `_in`. Direct calls in
`tests/runtime/test_fusion_tea_acceptance.py` migrate or are replaced by `CUT-TEAX-01`; temporary
Item-7 generated packages use final fields. No committed downstream package is changed.

| Stable ID | Maintained owner; generated/direct-caller consequence | Old → final generated field/call | Independent oracle |
|---|---|---|---|
| `FTGEN-01` | `tests/fixtures/fusion_tea/library/analyses/ife_lcoe.sysml`; `IFE_LCOEInputs.availability`; no direct `.run` call | `availability` → `availability_in` | `FT-01`, `CUT-FT-01`, `GOLDEN-01`; C25 is separately `CUT-C25-01`. |
| `FTGEN-02` | same file; `IFE_LCOEInputs.discount_rate`; no direct `.run` call | `discount_rate` → `discount_rate_in` | `FT-02`, `CUT-FT-01`, `GOLDEN-01`. |
| `FTGEN-03` | same file; `IFE_LCOEInputs.frequency`; no direct `.run` call | `frequency` → `frequency_in` | `FT-03`, `CUT-FT-01`, `GOLDEN-01`. |
| `FTGEN-04` | same file; `IFE_LCOEInputs.gain`; no direct `.run` call | `gain` → `gain_in` | `FT-04`, `CUT-FT-01`, `GOLDEN-01`. |
| `FTGEN-05` | same file; `IFE_LCOEInputs.om_cost_constant`; no direct `.run` call | `om_cost_constant` → `om_cost_constant_in` | `FT-05`, `CUT-FT-01`, `GOLDEN-01`. |
| `FTGEN-06` | same file; `IFE_LCOEInputs.plant_cost_constant`; no direct `.run` call | `plant_cost_constant` → `plant_cost_constant_in` | `FT-06`, `CUT-FT-01`, `GOLDEN-01`. |
| `FTGEN-07` | same file; `IFE_LCOEInputs.thermal_efficiency`; no direct `.run` call | `thermal_efficiency` → `thermal_efficiency_in` | `FT-07`, `CUT-FT-01`, `GOLDEN-01`; C2 is separately `CUT-C2-01`. |
| `FTGEN-08` | `tests/fixtures/fusion_tea/library/analyses/fusion_cycle.sysml`; `Recirculating_Power_FractionInputs.gain`; `tests/runtime/test_fusion_tea_acceptance.py` `.run` keyword | `gain` → `gain_in` | `FT-08`, `CUT-FT-01`; exact direct-call migration plus unchanged `f_recirc` in `GOLDEN-02`. |
| `FTGEN-09` | same model/caller; `Recirculating_Power_FractionInputs.thermal_efficiency`; `.run` keyword | `thermal_efficiency` → `thermal_efficiency_in` | `FT-09`, `CUT-FT-01`; exact direct-call migration plus unchanged `f_recirc` in `GOLDEN-02`. |
| `FTGEN-10` | same model; viability predicate input; no generated `.run` caller | `gain` → `gain_in` | `FT-10`, `CUT-FT-01`, independent C25/C2 negative sets. |
| `FTGEN-11` | `tests/fixtures/fusion_tea/library/analyses/hif_economics.sysml`; `Meier_Reactor_CostInputs.thermal_power_gw`; no direct `.run` call | `thermal_power_gw` → `thermal_power_gw_in` | `FT-11`, `CUT-FT-01`, `GOLDEN-01` and changed reactor record in `GOLDEN-02`. |
| `FTGEN-12` | same file; `Meier_COEInputs.availability`; no direct `.run` call | `availability` → `availability_in` | `FT-12`, `CUT-FT-01`, `GOLDEN-01`/`GOLDEN-02`; C25 remains separate. |
| `FTGEN-13` | same file; `Meier_COEInputs.net_electric_power_gw`; no direct `.run` call | `net_electric_power_gw` → `net_electric_power_gw_in` | `FT-13`, `CUT-FT-01`, `GOLDEN-01`/`GOLDEN-02`. |
| `FTGEN-14` | same file; `Meier_HIF_Driver_CostInputs.beam_energy_mj`; `tests/runtime/test_fusion_tea_acceptance.py` `.run` keyword | `beam_energy_mj` → `beam_energy_mj_in` | `FT-14`, `CUT-FT-01`; exact direct-call migration plus driver records in `GOLDEN-01`/`GOLDEN-02`. |
| `FTGEN-15` | same model/caller; `Meier_HIF_Driver_CostInputs.num_chambers`; `.run` keyword | `num_chambers` → `num_chambers_in` | `FT-15`, `CUT-FT-01`; exact direct-call migration plus driver records in `GOLDEN-01`/`GOLDEN-02`. |

### Script census

| ID | Explicit members | Disposition | Final owner/proof |
|---|---|---|---|
| `SCR-01` | `scripts/run_elaboration_corpus.py` | **DELETE/MIGRATE responsibility** | Replace with accepted-batch manifest driver owned by `CUT-CORP-01`; it invokes only public live/capture/v6 routes and never compares authorities. NR-01. |
| `SCR-02` | `scripts/capture_extraction_snapshots.py`, `capture_baseline_yaml.py`, `capture_pipeline_baselines.py`, `capture_filter.py` | **MIGRATE** | One v6 accepted-batch/capture driver plus route-neutral fixture filter. Baseline outputs are projected from API-01/05, never v5 rebuild. `CUT-CORP-01`, `CUT-V6-03`. |
| `SCR-03` | `scripts/_q5_debug.py`; probes `probe_alias_resolution.py`, `probe_backtracker_resolution.py`, `probe_item1_phase0.py`, `probe_item4_entrypoints.py`, `probe_item4_gate3.py`, `probe_item4_phase0.py`; spikes `spike_agg_wiring_h1_h4.py`, `spike_aggregation_validation.py`, `spike_backtracker_resolution_paths.py`, `spike_c11b_typed_dispatch.py`, `spike_c12_input_resolver.py`; `scripts/spikes/spike_bare_name_collisions.py`, `spike_chain_redef_rhs.py`, `spike_expose_pure_chain.py`, `spike_issue22_agg_ref.py`, `spike_output_registry_e2e.py`, `spike_reference_resolution.py`, `spike_virtual_instance_keys.py` | **DELETE** executable legacy mechanism probes | Durable research/kept exact tests own the learned behavior. Each maps respectively to `CUT-REG-01`, `CUT-SEL-01`, `CUT-CON-01`, `CUT-AGG-01`, `CUT-BIND-01`, or `CUT-RES-01`. NR-01/02/03. |
| `SCR-04` | `scripts/probes/probe_multiplicity_structure.py`, `probe_redefinition_structure.py`, `probe_sum_ast_structure.py`; top-level `spike_attribute_expressions.py`, `spike_classify_compilability.py`, `spike_compile_expressions.py`, `spike_extract_expression_asts.py`, `spike_hierarchy_ast.py`, `spike_resolve_expression_refs.py`; `scripts/spikes/_helpers.py`, `spike_design_attr_defaults.py`, `spike_template_binding_format.py`; `scripts/run_phase2.sh`, `run_phase3.sh`; `scripts/probes/README.md` | **RETAIN** only as parser/language learning utilities or historical instructions | NR-07 scans prove no deleted imports/symbols. If a member fails that gate, migrate it to exact primitives or delete it; retaining a compatibility adapter is forbidden. |
| `SCR-05` | `scripts/measure_item7_acceptance.py` (new) | **RETAIN** reproducibility driver | Non-production evidence only; public route outcome plus internal timing boundaries. `CUT-SCALE-01`, `CUT-TEAX-01`. |
| `SCR-06` | codegen `scripts/check_cutover_candidate.py` (planned) | **ADD/RETAIN** as the sole paired-candidate coordinator/checker | Owns `prepare`, `verify`, `promote-branches`, `publish-tags`, `recover-hard-block`, `verify-tags`, and `verify-release`; no second release/candidate checker. `CUT-PROMO-01/02/03`. |
| `SCR-07` | codegen `scripts/check_cutover_census.py`; `tests/unit/test_check_cutover_census.py` | **RETAIN** generated-inventory owner and its test-first contract | Deterministically enumerates both current worktrees, rejects uncensused marker paths, emits `cutover-inventory/v1`, and proves sorted/closed exact equality. `CUT-CENSUS-01`; NR-13. |
| `SCR-08` | codegen `scripts/check_cutover_residue.py`; `tests/unit/test_check_cutover_residue.py` | **RETAIN** self-safe structural residue owner and its test-first contract | Unicode-code-point rule vocabulary keeps the checker from matching itself; Python AST and non-Python scans distinguish executable residue from declared inventory. `CUT-RESIDUE-01`; NR-01 through NR-09 and NR-13. |

### Documentation census

| ID | Explicit members | Disposition | Final owner/proof |
|---|---|---|---|
| `DOC-01` | codegen `CLAUDE.md`; `docs/architecture/overview.md`; `docs/architecture/verification-matrix.md`; reference pages `00-pipeline-overview.md`, `02-orchestration.md`, `03-resolution-overview.md`, `04-producer-resolution.md`, `06-entry-point-classifier.md`, `07-graph-assembly.md`, `09-data-models.md`, `10-output-registry.md`, `11-analysis-backtracker.md`, `12-virtual-binding-rewrite.md`, `13-aggregation-scoping.md`, `15-naming-conventions.md`, `16-computed-attributes.md`, `18-literal-value-propagation.md`, `19-ast-dispatch-invariant.md`, `24-dual-resolution-architecture.md`, `25-hierarchy-resolver.md`, `27-snapshot-generation.md`, `30-diagnostic-severity.md` | **MIGRATE** all executable/current architecture descriptions to the sole exact route; remove deleted names and v5 mechanics. Historical `.project/**` evidence stays excluded. | `CUT-ABS-01`, NR-01 through NR-08 and NR-13. No document may present a deleted owner as callable. |

### Paired-candidate promotion census

| ID | Repository; exact member | Status and disposition | Required invariant / proof |
|---|---|---|---|
| `PROMO-01` | codegen `.project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json` | **PLANNED/ADD** singular canonical `elaborator-cutover-candidate/v1` record | One ID binds both GitHub origins, bases, content roots, normalized patches, complete path/hash inventories, batch/contracts/environment/TEAx, and schema-declared evidence-template hashes/pointers. The record self row is canonicalized; evidence ID slots use the one declared sentinel. No final-byte evidence hash participates in its own ID. `CUT-PROMO-01`. |
| `PROMO-02` | codegen `tests/unit/test_check_cutover_candidate.py` | **PLANNED/ADD** unit contract | Exact phase arguments; canonical payload/ID; record-self rule; deterministic evidence sentinel substitution; undeclared-ID refusal; acceptance/product tag object construction; input/type/origin/ref refusal. |
| `PROMO-03` | codegen `tests/integration/test_cutover_candidate_promotion.py` | **PLANNED/ADD** two-bare-authoritative-origin proof | Temporary remotes prove local worktrees are preparation-only; remote branch/tag CAS, observed/returned OIDs, second-origin compensation, hard-block refusal, authorized recovery, crash recovery, and release gate. `CUT-PROMO-02`. |
| `PROMO-04` | codegen `tests/conformance/test_cutover_candidate_workflows.py` | **PLANNED/ADD** static workflow/protection proof | Exact-set checks all six workflow callers and protected-ref requirements. `CUT-PROMO-03`. |
| `PROMO-05` | coordination `<state-dir>/<candidate_id>/promotion-journal.json` | **PLANNED/RUNTIME** durable canonical journal | Write/fsync/replace/parent-fsync state machine records every fresh authoritative observed/returned OID and exact CAS/compensation. `HARD_BLOCKED` or `TAGS_HARD_BLOCKED` fails every branch/tag/release gate until `recover-hard-block` restores an allowed paired terminal state. `CUT-PROMO-02`. |
| `PROMO-06` | coordination `<state-dir>/elaborator-cutover-promotion.lock` | **PLANNED/RUNTIME** named cross-repository filesystem lock | One exclusive advisory lock covers each remote branch/tag CAS pair, rollback/compensation, authorized recovery, and journal transition. It does not claim a physical two-repository transaction. `CUT-PROMO-02`. |
| `PROMO-07` | codegen `.github/workflows/elaborator-cutover-branch.yml` | **PLANNED/ADD** protected branch caller | Reciprocal agentic checkout; GitHub App `1cfe-elaborator-cutover-promoter` runs read-only `verify` then remote-CAS `promote-branches` against the two exact GitHub origins. |
| `PROMO-08` | agentic `.github/workflows/elaborator-cutover-branch.yml` | **PLANNED/ADD** reciprocal protected branch status caller | Checks the same ID and authoritative OIDs and requires codegen workflow result; branch rulesets forbid every non-App mutation. |
| `PROMO-09` | codegen `.github/workflows/elaborator-cutover-tags.yml` | **PLANNED/ADD** product-tag publisher | Promotion App runs `publish-tags` then post-publication `verify-tags` with reciprocal checkout; it is the sole writer of the protected product-tag namespace. |
| `PROMO-10` | agentic `.github/workflows/elaborator-cutover-tags.yml` | **PLANNED/ADD** reciprocal tag status caller | Same coordinator/ID, exact staged annotated objects, remote missing-ref CAS, compensation, and hard-block rules; missing or one-sided publication fails. |
| `PROMO-11` | codegen `.github/workflows/elaborator-cutover-release.yml` | **PLANNED/ADD** release caller | Runs `verify-release` against exact paired release manifest before packaging/publication. |
| `PROMO-12` | agentic `.github/workflows/elaborator-cutover-release.yml` | **PLANNED/ADD** reciprocal release caller | Requires the same `RELEASE_VERIFIED` journal and peer content-root/tag tuple. |
| `PROMO-13` | codegen local `refs/cutover/elaborator-cutover/<candidate_id>/prepared` | **PLANNED/HIDDEN PREPARATION REF** prepared codegen commit | Created local CAS from missing; content matches inventory/root/patch. It is an input to authoritative remote CAS, never itself a public landing. |
| `PROMO-14` | agentic local `refs/cutover/elaborator-cutover/<candidate_id>/prepared` | **PLANNED/HIDDEN PREPARATION REF** prepared agentic commit | Same local-only role and reciprocal record agreement; it carries no public authority. |
| `PROMO-15` | authoritative codegen `refs/tags/elaborator-cutover/accepted/<candidate_id>` | **PLANNED/OWNER ACCEPTANCE TAG** immutable annotated acceptance | Owner-only ruleset; targets PROMO-13 content; canonical annotation cites singular ID and codegen repository; published to `https://github.com/1cFE/sysml-codegen.git` by missing-ref CAS. |
| `PROMO-16` | authoritative agentic `refs/tags/elaborator-cutover/accepted/<candidate_id>` | **PLANNED/OWNER ACCEPTANCE TAG** reciprocal immutable acceptance | Targets PROMO-14 content, cites the same ID/repository set, and is published to `https://github.com/1cFE/agentic-mbse.git`; tags do not alter trees. |
| `PROMO-17` | codegen candidate-record `repositories.sysml-codegen.public_ref` | **PLANNED/PROTECTED REF INPUT** exact landing branch | Must equal recorded base before promotion and prepared commit after; required status `elaborator-cutover/candidate`; direct/force/delete/ordinary merge forbidden. |
| `PROMO-18` | agentic candidate-record `repositories.agentic-mbse.public_ref` | **PLANNED/PROTECTED REF INPUT** reciprocal landing branch | Same protection and paired state as PROMO-17. |
| `PROMO-19` | codegen `.project/active/elaborator-cutover/evidence/release-manifest.json` | **PLANNED/ADD** paired release input | Exact two repository/tag/content-root tuples; usable only after `TAGS_VERIFIED`. |
| `PROMO-20` | GitHub App `1cfe-elaborator-cutover-promoter` / installation identity `1cfe-elaborator-cutover-promoter[bot]` | **PLANNED/PROTECTED MUTATION IDENTITY** | Short-lived token comes only from `CUTOVER_PROMOTION_GITHUB_TOKEN`; both repositories install the App and branch/product-tag rulesets before prepare; local credentials are rejected for mutation phases. |
| `PROMO-21` | codegen and agentic protected product-tag refs bound by the candidate record | **PLANNED/STAGED REMOTE PUBLICATION** | `git mktag` creates exact local objects; the App publishes both by missing-ref remote CAS, compensates the first on second failure, hard-blocks failed compensation, then `verify-tags` reads both authoritative origins without mutation. |
| `PROMO-22` | `scripts/check_cutover_candidate.py recover-hard-block` | **PLANNED/AUTHORIZED RECOVERY PHASE** | Under the lock and App identity, branches may move only between each bound base/prepared OID and product tags only between absent/exact staged OID. It journals recovery/compensation and refuses foreign OIDs, ambiguity, absent acceptance, or wrong candidate without mutation. |

### Affected test responsibility census

| ID | Explicit members/responsibility | Disposition | Exact independent replacement |
|---|---|---|---|
| `TEST-01` | Exact retained suites: `test_elaboration_identity_foundation.py`, `test_elaboration_identity_vertical.py`, `test_elaboration_identity_collisions.py`, `test_elaboration_occurrence.py`, `test_elaboration_specialization_retypes.py`, `test_elaboration_payload_identity.py`, `test_elaboration_model_validation.py`, `test_elaboration_graph_roundtrip.py`, `test_elaboration_fail_closed.py`, `test_elaboration_projection.py`, `test_elaboration_projection_one_way.py`, `test_elaboration_generation_boundary.py`, `test_elaboration_public_mutation.py`, `test_elaboration_aggregations.py`, `test_elaboration_computed_attrs.py`, `test_elaboration_plural_scope.py`, `test_elaboration_shadowing.py`, `test_elaboration_sibling_channels.py`, `test_elaboration_expose_shapes.py`, `test_elaboration_phase5_remediation.py`, `test_elaboration_import_boundaries.py`, `test_literal_totality.py`, `test_upstream_pins.py`, `test_elaboration_contract_matrix.py` | **RETAIN/MIGRATE public route setup only.** No test may import API-03 or legacy owners. | Their authored exact-ID/shape expectations remain independent; supplement with `CUT-OCC-01`, `CUT-PROJ-01`, `CUT-RES-01`. |
| `TEST-02` | Dual/wrong-oracle files: `test_elaboration_dual_run.py`, `test_elaboration_corpus_ledger.py`, `test_elaboration_spike_parity.py` F26 comparison only, `test_dual_resolution.py`, `test_default_lane_disagreement.py`, `test_calc_compat_parity.py` coexistence only, `test_constraint_profile_route_parity.py` coexistence only, `test_legacy_snapshot_closure.py`, `test_grandfather_carveout.py`, `test_snapshot_v5_gate.py`, `test_dead_code_removal.py` old list | **DELETE wrong-oracle responsibilities.** Keep C19 structural proof under `CUT-C19-01`; keep arithmetic under the exact core. | F26 literal oracle → `CUT-F26-01`; parity → `CUT-V6-03`; absence → `CUT-ABS-01`; resolution → `CUT-RES-01`; compiler → `CUT-COMP-01`; v5 → `CUT-V6-02`. One behavior per ID, no legacy execution. |
| `TEST-03` | Snapshot/public-route files: `test_extraction_snapshots.py`, `test_snapshot_contract.py`, `test_snapshot_generation.py`, `test_snapshot_constraint_parity.py`, `test_constraint_snapshot_identity.py`, `test_constraint_snapshot_portability.py`, `test_fingerprint_stability.py`, `test_whole_tree_portability.py`, `test_source_identity_routes.py`, `test_snapshot_envelope_gate.py`, `test_source_referent.py`, `test_source_referent_shape_gate.py`, `test_cli_generation.py`, `test_orchestrator.py`, `test_generation_boundary.py`, `test_pipeline_e2e.py`, `test_parallel_validation.py` | **MIGRATE** to public live/capture/in-place/relocated v6. Delete assertions about v5 extraction fields, sidecars, lowering modes, wide context, or rebuild internals. | `CUT-API-01/02`, `CUT-CLI-01`, `CUT-V6-01/02/03`, `CUT-CAP-01`, `CUT-PAY-01`. |
| `TEST-04` | Independently useful legacy mechanism files: conformance `test_backtracker.py`, `test_agg_key_forms.py`, `test_agg_localterm_default.py`, `test_aggregation_scoping.py`, `test_alias_agg_probe_generation.py`, `test_computed_attributes.py`, `test_constraint_lowering.py`, `test_constraint_lowering_integrity.py`, `test_constraint_migration_mapping.py`, `test_constraint_pipeline_threading.py`, `test_fusion_tea_snapshot.py`, `test_graph_assembly.py`, `test_output_registry.py`, `test_parameter_group_deriver.py`, `test_part_instance_index.py`, `test_producer_completeness_acceptance.py`, `test_self_named_rescue.py`, `test_shared_producer_convergence.py`, `test_virtual_binding_rewrite.py`; unit `test_backtracker_aggregation.py`, `test_backtracker_computed_attrs.py`, `test_dependency_backtracker.py`, `test_graph_builder.py`, `test_graph_builder_aggregation.py`, `test_graph_builder_computed_attrs.py`, `test_graph_builder_zero_default.py`, `test_output_registry.py`, `test_output_registry_construction.py`, `test_parameter_groups.py`, `test_part_instance_index.py`, `test_producer_completeness.py`, `test_producer_qn_rule.py`, `test_producer_resolution_table.py`, `test_rewrite_virtual_bindings.py`, `test_supplied_values.py`, `test_uncovered_params.py`, `test_virtual_binding_rewrite.py` | **DELETE mechanism assertions; migrate each useful behavior, not files wholesale.** | Backtracking/target → `CUT-SEL-01`; aggregation → `CUT-AGG-01`; binding/VBR → `CUT-BIND-01`; C19 supplied value → `CUT-C19-01`; registry/groups → `CUT-REG-01`; occurrence → `CUT-OCC-01`; resolution/completeness → `CUT-RES-01`; assembly/uncovered → `CUT-PROJ-01`; constraint → `CUT-CON-01`. |
| `TEST-05` | Constraint/expression useful oracles: `test_compile_calc_def_golden.py`, `test_expression_compiler.py` (unit and conformance), `test_expression_reconstruction_fidelity.py`, `test_modeled_default_fidelity.py`, `test_constraint_non_numerical.py`, `test_constraint_occurrence_demand_acceptance.py`, `test_constraint_occurrence_demand_supplementary.py`, `test_constraint_generation_live.py`, `test_constraint_generation_integration.py`, `test_constraint_name_safety_routes.py`, execution constraint tests | **RETAIN/MIGRATE** to exact compiler/facts/profile and public routes. Delete only imports/coexistence fields. | Hand-authored expressions, IDs, predicate outcomes, and numeric execution remain. `CUT-COMP-01`, `CUT-CON-01`, `CUT-TEAX-01`. |
| `TEST-06` | Runtime/customer files: `tests/runtime/test_fusion_tea_acceptance.py`, `tests/runtime/pipeline_runner.py`, `tests/conformance/test_fusion_tea_snapshot.py`, `tests/helpers/registry_compat.py`, plus real execution suites | **MIGRATE.** Delete stub-based Item-7 acceptance and v5 graph rebuild. Route generic tests may keep their stub if they do not claim Item-7 proof. | Fusion Tea Item-7 acceptance is only `CUT-FT-01`, `CUT-C25-01`, `CUT-C2-01`, `CUT-TEAX-01`, `CUT-SCALE-01`. Existing independent arithmetic constants may be moved, not recomputed from runtime output. |
| `TEST-07` | Unaffected files proven absent from `cutover-inventory/v1` | **RETAIN outside the affected allowlist.** This row owns no affected member and cannot absorb a discovered path. | Exact inventory equality fails if an affected file is hidden here. |

### Stable affected-test and golden child rows

These child IDs split responsibilities that the broad rows above cannot safely group. A path may
appear more than once only when the `symbol/responsibility` column separates distinct code in that
file.

| ID | Repository path; symbol/responsibility | Exact disposition | Final owner and independent proof |
|---|---|---|---|
| `TEST-02.01` | codegen `tests/unit/test_occurrence_roundtrip_parity.py`; both v5/FrozenOccurrenceIndex parity cases | **DELETE** both wrong-oracle tests | V6 codec round trip is `CUT-V6-01`; exact occurrence corruption is `CUT-OCC-01`/`CUT-V6-02`. No live-ID parity. |
| `TEST-03.01` | codegen `tests/conformance/test_constraint_catalog_determinism.py`; public catalog determinism | **MIGRATE** setup to API-01 | Literal catalog IDs/order remain the oracle under `CUT-CON-01`; no legacy builder. |
| `TEST-03.02` | codegen `tests/conformance/test_diagnostic_screen.py:60-113`; render/typed diagnostic expectations | **RETAIN/MIGRATE** to exact diagnostic owner | Exact code/data/order assertions remain under `CUT-CAP-01`; no screen/lowering ordering oracle. |
| `TEST-03.03` | codegen `tests/conformance/test_diagnostic_screen.py:119-155`; live/v6 halt behavior | **MIGRATE** to staged public live/capture routes | `CUT-SRC-01`, `CUT-CAP-01`, and `CUT-V6-02`. |
| `TEST-03.04` | codegen `tests/conformance/test_diagnostic_screen.py:158-188`; screen-before-lowering spy | **DELETE** old-order test | Replacement is strict admission/diagnostic/elaboration failure order in `CUT-CAP-01`/`CUT-V6-02`. |
| `TEST-03.05` | codegen `tests/conformance/test_sanitize_invariance.py`; generated-name invariance | **MIGRATE** to exact projector | Literal names remain independent under `CUT-PROJ-01`. |
| `TEST-04.01` | codegen `tests/conformance/test_factory_calc_usage.py:177-552`; `_build_pipeline_module` factory | **DELETE** legacy factory mechanism | Public module/input/output behavior moves to `CUT-PROJ-01`. |
| `TEST-04.02` | codegen `tests/unit/test_hygiene_tail_agg_compile.py:54-62`; literal compiled strings | **RETAIN/MIGRATE** strings to exact compiler | `CUT-AGG-01`/`CUT-COMP-01`; delete registry/legacy graph-builder setup. |
| `TEST-04.03` | codegen `tests/unit/test_matcher_fixes_item7.py:106-160`; positive/negative consumer sets | **RETAIN/MIGRATE** consumer oracle | `CUT-RES-01`; delete backtracker/key-table setup. |
| `TEST-05.01` | codegen `tests/conformance/test_catalog_definition_join.py:24-87`; catalog FK/usage-tier invariants | **MIGRATE** to canonical live builder and delete the transitional flag | `CUT-CON-01`. |
| `TEST-05.02` | codegen `tests/conformance/test_catalog_no_reconstruction.py`, `test_extractor.py`, `test_gate_a_owner_classification.py`, `test_source_identity_extraction.py`; exact catalog/extraction facts | **RETAIN/MIGRATE** to unsuffixed identified route | `CUT-CON-01`; each literal ID/owner/shape remains the oracle. |
| `TEST-05.03` | codegen `tests/unit/test_concrete_constraint_model.py`, `test_constraint_usage_preparation.py`, `test_phase4_bugfix_regressions.py`; ID minting/profile refusal | **MIGRATE** useful assertions and delete lowering transcripts | Neutral ID helper plus exact fact/profile boundary under `CUT-CON-01`. |
| `TEST-03.06` | codegen `tests/conformance/conftest.py`; shared live/context fixture | **MIGRATE** to API-01 and private test data only | Its dependent tests use their named replacement; fixture cannot construct context or invoke a legacy owner. |
| `TEST-03.07` | codegen `tests/conformance/test_ast_dispatch_invariant.py`, `test_computed_attribute_golden.py`, `test_hierarchy_resolver.py`; indirect `conftest.py` consumers | **MIGRATE** setup only | Existing literal AST/arithmetic/hierarchy expectations map to `CUT-COMP-01`, `CUT-AGG-01`, `CUT-PROJ-01`. |
| `TEST-03.08` | codegen `tests/unit/test_capture_fixtures_filter.py`; capture helper/filter | **MIGRATE** to staged capture and original display-path filter | `CUT-SRC-01`/`CUT-CAP-01`. |
| `TEST-03.09` | codegen conformance `test_deep_cross_scope_probe.py`, `test_formula_quoted_owner.py`, `test_gen_json_templates.py`, `test_gen_module_wrappers.py`, `test_gen_pipeline_yaml.py`, `test_gen_registry.py`, `test_gen_schemas.py`, `test_gen_stencils.py`, `test_pipeline_module_expansion.py`, `test_type_mapping_consolidation.py`, `test_written_qualifier_anchoring.py`; generation/public route users | **MIGRATE** setup to API-01 | Existing literal generated-output assertions remain under `CUT-PROJ-01`/`CUT-REG-01`. |
| `TEST-03.10` | codegen execution `test_constraint_def_owned_redefining_execution.py`, `test_constraint_execution.py`, `test_constraint_occurrence_demand_execution.py`, `test_gate_a_execution.py`; runtime constraint routes | **MIGRATE** setup to API-01 | Existing numeric/decision outcomes remain under `CUT-CON-01`; no legacy front end. |
| `TEST-03.11` | codegen `tests/unit/test_exit_point_aliases.py`; generated exit aliases | **MIGRATE** setup to exact projector | Literal alias oracle under `CUT-REG-01`. |
| `TEST-04.04` | codegen conformance `test_crosspart_rollup_twolevel.py`, `test_entry_point_classifier.py`, `test_factory_aggregation.py`, `test_factory_formula.py`, `test_factory_purity.py`, `test_ife_plant.py`, `test_matcher_reclassification.py`, `test_plant_value_shapes.py`, `test_plant_values.py`, `test_res08_consumer_scope_paths.py`, `test_return_style_extraction.py`, `test_self_named_binding_trap.py`, `test_sibling_channel_ambiguity.py`, `test_silent_failure_family1.py`, `test_silent_failure_sc4a1.py`, `test_spec_chain_channel.py`, `test_spec_chain_twolevel.py`; useful semantics behind legacy setup | **DELETE** mechanism assertions and **MIGRATE** only named literal behavior | `CUT-AGG-01`, `CUT-BIND-01`, `CUT-RES-01`, `CUT-SEL-01`, `CUT-OCC-01`, or `CUT-PROJ-01` according to each existing assertion. |
| `TEST-04.05` | codegen integration `test_bug2_regression.py`, `test_computed_attribute_pipeline.py`, `test_e2e_output_registry.py`, `test_full_pipeline.py`, `test_hierarchy_e2e.py`, `test_output_registry_smoke.py`; customer pipeline behavior | **MIGRATE** to public exact route and delete registry setup | Existing numeric/generated outputs map to `CUT-PROJ-01`, `CUT-REG-01`, `CUT-AGG-01`. |
| `TEST-04.06` | codegen unit `test_computed_attribute_extraction.py`, `test_constraint_graph_extension.py`, `test_constraint_resolver.py`, `test_design_overrides_threaded.py`, `test_hierarchy_pipeline.py`, `test_logical_demand_resolution.py`, `test_silent_failure_family2_family3_fires.py`, `test_silent_failure_family3.py`, `test_warning_reconciliation.py`; useful legacy-mechanism behavior | **DELETE** old fixtures/mechanisms and **MIGRATE** literal behavior | One-to-one owners are `CUT-AGG-01`, `CUT-CON-01`, `CUT-RES-01`, `CUT-C19-01`, or `CUT-PROJ-01`; inventory rows keep each exact path visible. |
| `TEST-01.01` | codegen `tests/conformance/test_wi014_toy.py`; F26 | **DELETE** old v5/registry parity and **MIGRATE** the file to an independent literal test | Sole owner `CUT-F26-01`; route parity is separately `CUT-V6-03`, absence `CUT-ABS-01`. |
| `TEST-01.02` | codegen `tests/unit/test_output_aliases.py`; public aliases | **MIGRATE** setup to exact projector | Literal alias tuples remain under `CUT-REG-01`. |
| `TEST-01.03` | codegen `tests/conformance/test_data_models.py`; generation DTO assertions versus legacy registry/backtracking/group rows | **RETAIN** `ComputationGraph` DTO assertions; **DELETE/MIGRATE** legacy rows | `CUT-PROJ-01`; the row is split by symbol in the generated inventory. |
| `GOLDEN-01` | codegen `tests/fixtures/golden/calc_def_compilation_golden.json`; 15 affected result records | **MIGRATE** expected generated expressions to final formal names | Independent arithmetic/source formulas under `CUT-ARITH-01`; affected records are ten IFE LCOE results, Meier COE `coe_cents_kwh`, driver `bank_energy_joules`/`cost_billions`, reactor `reactor_cost_billions`, and recirculating `fusion_cycle_gain`. |
| `GOLDEN-02` | codegen `tests/fixtures/golden/calc_compat_parity_golden.json`; three changed direct records plus controls | **MIGRATE** Meier COE `coe_cents_kwh`, driver `cost_billions`, and reactor `reactor_cost_billions` | `CUT-ARITH-01`; unchanged independent controls remain IFE LCOE `lcoe`, driver `gamma`, and recirculating `f_recirc`. |
| `AGENTIC-TEST-01` | agentic `tests/test_sysml/test_constraint_extraction.py`, `test_constraint_extraction_ordering.py`, `test_constraint_fact_shapes.py`; identified extraction facts/order | **MIGRATE** to sole unsuffixed identified extraction | Exact IDs, order, and fact shape under `CUT-CON-01`; transitional export absent by NR-08. |
| `AGENTIC-TEST-02` | agentic `tests/test_sysml/test_executable_profile.py`, `test_executable_profile_arithmetic.py`, `test_executable_profile_v3.py`, `test_executable_profile_v4.py`; profile association/evaluation | **MIGRATE** to `evaluate_profile(IdentifiedConstraintFacts)` | Exact decisions/arithmetic under `CUT-CON-01`; delete QN selection oracle. |
| `AGENTIC-TEST-03` | agentic `tests/test_sysml/test_expression_ir_extraction.py`, `test_public_api_exports.py`; IR and exports | **RETAIN/MIGRATE** exact IR and final unsuffixed exports | Schema pins plus `CUT-CON-01`; transitional symbols absent by NR-08. |
| `AGENTIC-TEST-04` | agentic `tests/test_validation/test_item12_checks.py`, `test_level4_reconciliation.py`; validation callers | **MIGRATE** to already identified `item.decision` | Existing validation outcomes remain; no QN lookup/selection. `CUT-CON-01`, NR-08. |

`TEST-04` is the required anti-blanket rule: each old suite's useful behavior maps to a distinct
replacement ID. Passing the 29 cells alone does not authorize deletion.

## Exact 37-Path Accepted-Batch Manifest Contract

The table fixes population and allowed candidate outcome. “V6 graph” means public live generation,
capture, in-place load, and relocated load all succeed and agree. A diagnostic means live returns the
named typed diagnostic, capture refuses, and no snapshot exists. Actual counts/digests are written
beside these rows only in the single owner-reviewed candidate; an unexpected outcome is a failed
gate, never an automatic update.

`agg_literal_probe` was previously named here as the required non-R7 control. It is not one.
**[OWNER 2026-08-10] Modeled aggregation is accepted as executable** (re-verified on the clean
Item 6 baseline in recovery Phase 2). Its Item-5 `CodeGenerationError` came from the
pre-elaboration calc-def presence gate, so a route that reaches the elaborator must produce a V6
graph for it. The no-calculation-definition control responsibility moves to a genuinely empty
fixture. See the B37-01 ruling in
`.project/completed/20260809_elaborator-breadth/diff-ledger.md`.

| ID | Fixture path | Required candidate outcome | Governing contract/class |
|---|---|---|---|
| `B37-01` | `agg_literal_probe` | V6 graph, with the `5.0` literal operand observed | Accepted expected-fix; modeled aggregation is executable **[OWNER 2026-08-10]** |
| `B37-01c` | genuinely empty control fixture (Phase 3/4) | `CodeGenerationError`: no calculation definition; no snapshot | Non-R7 expected-collapse control |
| `B37-02` | `agg_localterm_probe` | `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-03` | `alias_agg_probe` | `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-04` | `attr_expr_probe` | V6 graph | Accepted expected-fix; modeled expression runtime behavior |
| `B37-05` | `catf_mfe_model` | `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-06` | `chain_override_probe` | 2× `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-07` | `chain_spike_model` | 3× `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-08` | `constraint_inline` | V6 graph | Accepted expected-fix; exact occurrence predicate |
| `B37-09` | `constraint_multi_instance` | V6 graph | Accepted expected-fix; independent instances |
| `B37-10` | `constraint_non_numerical` | V6 graph | Accepted expected-fix; numerical execution/string exclusion |
| `B37-11` | `crosspart_rollup_twolevel` | `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-12` | `d38_caret` | V6 graph | C17/C26 finite multiplicity accepted fix |
| `B37-13` | `deep_cross_scope_probe` | V6 graph | C5/DCS exact producer-edge accepted fix |
| `B37-14` | `expression_binding_probe` | 6× `SI_EXPRESSION_SOURCE_UNSUPPORTED` + 3× `SI_SELF_BINDING`; no snapshot | C22 + SRC-01 expected-collapse |
| `B37-15` | `fusion_tea` | V6 graph after exactly 15 in-place D-5 renames | C2, C25, F19; owner-ratified correction |
| `B37-16` | `gate_a` | 2× `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-17` | `gate_a_package_owner` | 2× `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-18` | `ife_plant` | 21× `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-19` | `invocation_binding_probe` | `SI_EXPRESSION_SOURCE_UNSUPPORTED`; no snapshot | C22 expected-collapse |
| `B37-20` | `issue22_model` | `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-21` | `modeled_default_fidelity` | V6 graph | Accepted expected-fix; total defaults |
| `B37-22` | `plant_value_shapes` | 2× `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-23` | `plant_values` | `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-24` | `quoted_owner_formula` | V6 graph | Expected-collapse equal control |
| `B37-25` | `return_styles` | 3× `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-26` | `retype_model` | V6 graph | Most-specific writer accepted fix |
| `B37-27` | `sample_model` | V6 empty graph | Expected-collapse byte/semantic empty control |
| `B37-28` | `self_named_binding_trap` | `SI_SELF_BINDING`; no snapshot | Direct SRC-01 negative |
| `B37-29` | `self_named_rescue` | `SI_SELF_BINDING`; no snapshot | Prohibited rescue removed |
| `B37-30` | `shadowed_reference` | V6 graph | C20 parser-resolved referent accepted fix |
| `B37-31` | `shared_producer` | 2× `SI_SELF_BINDING`; no snapshot | SRC-01 calc/constraint expected-collapse |
| `B37-32` | `sibling_channel_ambiguity` | `SI_SELF_BINDING`; no snapshot | SRC-01 expected-collapse |
| `B37-33` | `solar_battery_model` | 24× `SI_SELF_BINDING`; no snapshot | Finite multiplicity then SRC-01 |
| `B37-34` | `spec_chain_channel` | `SI_SELF_BINDING`; no snapshot | SRC-01 inherited binding |
| `B37-35` | `spec_chain_twolevel` | `SI_SELF_BINDING`; no snapshot | SRC-01; C21 remains focused-fixture proof |
| `B37-36` | `unresolvable_attr_probe` | V6 graph | Nine modeled formulas accepted fix |
| `B37-37` | `wi014_toy` | V6 graph | Stable-ID/source-key accepted fix |

The population is exactly 37 unique paths: 14 V6 graphs, 22 capture refusals, and one non-R7
no-calculation-definition control. `C19` is not smuggled into this population; it remains the
separate named maintained fixture/test `CUT-C19-01`. The candidate status is
`pending-owner-acceptance`. That is a known gate state, not an unresolved design decision. Only an
explicit recorded `accepted` disposition permits the final commit.

## No-Residue and Closure Gates

All commands run from `sysml-codegen`. Expected-empty `rg` commands pass only with exit code 1.
Historical `.project/` artifacts are deliberately outside the scanned roots.

| Gate | Exact check and required result |
|---|---|
| `NR-01` | `rg -n 'build_elaborated_pipeline|elaboration\.diff|run_elaboration_corpus|dual.run|legacy.*exact|exact.*legacy' src tests scripts` → empty except prose in the sole static absence test. |
| `NR-02` | `rg -n 'PartInstanceIndex|\bPathStep\b|\bInstanceOccurrence\b|rewrite_virtual_bindings|self_named_rescue|_rescue_self_named_bindings|specialized.chain|virtual.*calc.*usage' src tests scripts` → empty. Exact `OccurrenceRecord` is allowed. |
| `NR-03` | `rg -n 'DependencyBacktracker|OutputRegistry|build_output_registry|build_computation_graph|collect_uncovered_params|producer_resolution|producer_completeness|supplied_values|constraint_lowering' src tests scripts` → empty, including imports and logger names. |
| `NR-04` | `rg -n 'SNAPSHOT_FORMAT_VERSION\s*=\s*5|extraction_snapshot|load_extraction_snapshot|serialize_extraction_snapshot|snapshot_to_json|build_full_graph_from_snapshot|build_classifier_inputs_from_snapshot|GrandfatheredSnapshotError|grandfathered_off|constraint_lowering_mode' src tests scripts docs pyproject.toml` → empty. `find tests/fixtures -name extraction_snapshot.json` returns only accepted v6 runtime rows, each with top-level version 6. |
| `NR-05` | `rg -n 'compile_calc_def_exact|coexistence|id_sidecar|_by_id_sidecar|extract_constraint_facts_(neutral|identified).*extract_constraint_facts_(neutral|identified)' src tests ../agentic-mbse/src ../agentic-mbse/tests` → empty. One identified extraction symbol and one compiler core may remain under their final unsuffixed names. |
| `NR-06` | A focused import test asserts orchestration/generation/initialization aliases are object-identical; snapshot exports equal the API-13 allowlist; root exports none; constructing context with each old field raises `TypeError`. |
| `NR-07` | `rg -n 'sysml_codegen\.(analysis\.(dependency_backtracker|part_instance_index|constraint_lowering)|core\.output_registry|resolution\.(graph_builder|producer_resolution|producer_completeness|supplied_values)|snapshot\.(loader|serializer|graph_rebuild)|orchestration\.elaborated_pipeline)' src tests scripts` → empty. A reverse import-boundary test proves elaboration and generation models do not adapt deleted owners. |
| `NR-08` | `.venv/bin/python scripts/check_cutover_residue.py --repo codegen=. --repo agentic=../agentic-mbse --inventory .project/active/elaborator-cutover/cutover-inventory.json --rule item6-dual-2 --expect absent` proves the old QN association entry point, export, definition, and calls are absent; validation levels 4 and 6 consume the identified exact association result; any separately named formatter accepts only already-decided exact data and its AST contains no qualified-name lookup, candidate selection, or decision construction. During design closure the same command with `--expect inventoried` returned exactly five declared transitional hits. Exact fact/profile/IR versions match `_upstream_pins.py`; boundary guards remain deny-by-default. |
| `NR-09` | `rg -n '^\s*in\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\1\s*;' tests/fixtures/fusion_tea --glob '*.sysml'` is implemented with a backreference-capable checker and returns zero; `CUT-FT-01` independently counts exactly 15 approved `_in = original_bare_name` mappings. |
| `NR-10` | `CUT-CORP-01` reads this `B37-*` table and the candidate manifest: exactly 37 stable IDs/paths, no duplicate, no extra fixture, 14 v6/22 refusal/1 non-R7 control, zero v5, zero unclassified semantic diff, and owner disposition `accepted` before final commit. |
| `NR-11` | `CUT-TEAX-01` fails if `tests.runtime.pipeline_runner`, a monkeypatch/stub, private registry helper, or compatibility API is imported. It asserts both verifiers, public registry construction, real `execute_pipeline`, LCOE, and C25/C2 mutations on live and relocated packages. |
| `NR-12` | `rg -n 'T[B]D|TO[B]EDECIDED|PLACE[H]OLDER' .project/active/elaborator-cutover/design.md .project/active/elaborator-cutover/cutover-census.md` → empty. The split spelling prevents the gate from matching itself. |
| `NR-13` | Run the exact `inventory` and `compare` commands in Closure Method, then `.venv/bin/python scripts/check_cutover_residue.py --repo codegen=. --repo agentic=../agentic-mbse --inventory .project/active/elaborator-cutover/cutover-inventory.json --rule all --expect inventoried` for the certified current worktrees. Design evidence is 231 closed/sorted rows, 78 marker-discovered paths, and 363 inventoried transitional hits. Candidate closure changes only the last flag to `--expect absent` and requires zero hits. |

## Quality and Commit Closure

The implementation keeps this census current by marking each stable row complete only after its
replacement test and residue gate pass. It records fresh test/Ruff/mypy counts for both repositories,
all licensed tests collected without license skips, `git diff --check`, the exact 37 candidate, scale
evidence, TEAx state, and owner disposition.

Preparatory commits are non-releasable. The final codegen commit must contain API-01 through API-14,
PROD-01 through PROD-24, SCR-01 through SCR-08, affected test migrations, `FIX-01`, the accepted
`B37-*` manifest/artifacts, and every residue gate. It records and pins the coordinated
agentic-mbse commit containing PROD-20 through PROD-22. Neither side may be merged, tagged, or called
complete without the other. This is the mechanical meaning of an atomic cutover across two Git
repositories.
