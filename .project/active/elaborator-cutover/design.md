# Design: Elaborator Atomic Cutover

- **Status:** Draft — DR3 bounded corrections are durable and mechanically verified; focused rereview pending
- **Owner:** Reid W
- **Created:** 2026-08-10
- **Updated:** 2026-08-10
- **Branch:** `source-identity-epic`
- **Commit at design:** `1672c57`
- **Epic:** ELABORATE-FIRST, Item 7

## Overview

Item 7 makes the resolved exact-ID `InstanceGraph` the only semantic authority used by
live generation, snapshot capture, and offline generation. It replaces extraction snapshot v5
with an integrity-bound v6 instance-graph envelope, migrates the maintained Fusion Tea model,
and deletes the legacy reconstruction route in one accepted landing.

## Related Artifacts

- [Spec](spec.md) and its [first](spec-review.md) and [v2](spec-review-v2.md) reviews. The three
  v2 findings are amended in the spec and were objectively verified before this design.
- [Product-lens ledger](product-lens.md), whose gate is clear.
- [Epic Item 7 and owner rulings](../../backlog/epic_elaborate_first_architecture.md).
- [Shared elaborator spec](../elaborator-design/spec.md),
  [design](../elaborator-design/design.md), and
  [design review](../elaborator-design/design-review.md).
- [Item-6 identity and cutover research](../../research/20260809-153245_item6-identity-completion-and-cutover-census.md)
  and [instance-graph architecture research](../../research/20260807-145336_elaborate-first-instance-graph-architecture.md).
- Item-6 certified [spec](../../completed/20260810_elaborator-identity-completion/spec.md),
  [design](../../completed/20260810_elaborator-identity-completion/design.md),
  [plan](../../completed/20260810_elaborator-identity-completion/plan.md), and
  [audit](../../completed/20260810_elaborator-identity-completion/audit_v3.md).
- [Item-5 37-path diff ledger](../../completed/20260809_elaborator-breadth/diff-ledger.md) and the
  inherited 29-cell contract at
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`.
- [Closed cutover census](cutover-census.md), which is part of this design contract.

No ADR index exists, so this design conflicts with no active decision record.

Additional shaping is skipped because the epic, two architecture designs, Item-6 research,
certified implementation, and reviewed Item-7 spec already settle the problem and its boundaries.
Product design is skipped because this is an authority and persistence cutover. The public CLI and
Python capabilities are already specified; there is no new consumer workflow or unresolved
interaction to shape. The product-lens review independently found the contract clear.

## The Point

**[NEED, inherited from owner rulings and the epic]** One loaded semantic source occurrence must
become exactly one runtime source for every and only its bound consumers. The same answer must
survive live generation and portable offline generation. Unsupported authored forms must fail
before capture or generation. A legacy front end that can invent a different answer defeats that
obligation even when tests happen to agree, so the cutover is complete only when the resolved
instance graph is the sole shipped authority.

## Research Findings

- The shipped builder still performs extraction, name-based repair, backtracking, compilation, and
  legacy graph assembly in one function (`src/sysml_codegen/orchestration/pipeline_builder.py:833`).
  It returns the wide legacy context at `pipeline_builder.py:1159`.
- `PipelineContext` carries intermediate extractors, registries, maps, and lowering state that
  generation does not need (`src/sysml_codegen/orchestration/pipeline_context.py:74`). Production
  generation consumes `computation_graph`; `calc_defs` supplies one log count and
  `constraint_lowering_mode` supplies only the v5 grandfather gate
  (`src/sysml_codegen/cli/__init__.py:978`).
- The exact route already builds a strict graph and projects it, but it is an internal parallel
  wrapper (`src/sysml_codegen/orchestration/elaborated_pipeline.py:22`). This is the right mechanism
  under the wrong owner.
- `InstanceGraph` contains occurrences, attributes, calculations, constraints, exact input edges,
  and diagnostics, and validates its own referential integrity
  (`src/sysml_codegen/elaboration/graph.py:233`, `graph.py:245`). It refuses projection when any
  blocking diagnostic remains (`graph.py:683`).
- Projection already has the required one-way boundary: it accepts `InstanceGraph`, renders names,
  and returns `ComputationGraph` (`src/sysml_codegen/elaboration/project.py:1`,
  `project.py:1062`). Its remaining import from legacy constraint lowering is ownership debt, not a
  reason to keep that module (`project.py:28`).
- The Item-6 graph codec already uses deterministic, sorted JSON, a schema marker, SHA-256, exact-ID
  payload fields, and post-decode graph validation
  (`src/sysml_codegen/snapshot/instance_graph.py:63`, `instance_graph.py:73`,
  `instance_graph.py:751`). V6 wraps and hardens that payload; it does not invent another graph.
- Source paths already have a portable ordered-root form and strict percent-encoding validation
  (`src/sysml_codegen/analysis/source_referent.py:32`, `source_referent.py:62`). The helper belongs
  with the v6 source manifest.
- The CLI already makes `--models` and `--from-snapshot` mutually exclusive, preserves the output,
  package, overwrite, regeneration, and filter options, and rejects applying the live filter to a
  snapshot (`src/sysml_codegen/cli/__init__.py:693`, `cli/__init__.py:846`).
- The maintained Fusion Tea model contains exactly 15 same-named self-bindings: ten in generic IFE,
  three in HIF plant, and two in HIF driver. The affected definitions and equations are local to the
  three maintained analysis files (`tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml:98`,
  `designs/hif_ife/hif_plant.sysml:177`, `designs/hif_ife/hif_driver.sysml:62`).
- The current Fusion Tea execution test uses a simulated TEAx surface. It provides good independent
  arithmetic constants but cannot satisfy the Item-7 real-TEAx proof
  (`tests/runtime/test_fusion_tea_acceptance.py:1`). Existing execution tests show the required
  public registry and `execute_pipeline` calling pattern
  (`tests/execution/test_constraint_execution.py:91`).
- The Item-6 dirty state in both coordinated repositories is certified prerequisite work. This
  design does not modify production or test code.

## Core Concept

The system is one load-and-elaborate pipeline followed by one projection. Live generation runs both
steps. Capture runs the first step once and stores its validated result. Offline generation loads
that same result and runs the same projection. `InstanceGraph` is the sole semantic authority;
`ComputationGraph` is a disposable code-generation plan derived from it. A narrow
`PipelineContext` preserves the public `.computation_graph` capability, but it never accepts or
exposes a mutable graph pair. It stores canonical instance bytes, canonical selection, and a
projection receipt privately. Each graph view is freshly decoded and reprojected. The v6 envelope
binds the graph, compatibility markers, capture options, provenance, and the exact staged source
bytes parsed by SysIDE. The accepted paired candidate changes the authorities, exports, snapshots,
fixtures, tests, and deletions together.

## Key Bets

- **B1. Exact-ID elaboration contains the complete semantic answer required for generation.** The
  certified Item-6 payload, graph, formal provenance, and projection results support this. *If
  false → deleting a legacy reconstruction mechanism loses supported behavior rather than deleting
  a second authority.*
- **B2. The 29-cell contract plus independently anchored legacy-suite replacements cover the useful
  behavior of the old front end.** *If false → the cutover can pass its matrix while losing a
  behavior that had an independent product oracle.*
- **B3. A self-contained graph snapshot is useful without its original source tree.** Source hashes
  prove what was captured; optional source-root verification proves whether a supplied tree still
  matches. *If false → relocated offline generation would need source access and would no longer be
  a portable snapshot route.*
- **B4. Fusion Tea's fifteen D-5 renames preserve physics while exposing the intended source
  referents.** The equations use the same values after the formal identifiers are renamed. *If
  false → the customer-scale execution result changes for a reason other than source binding.*

## Key Decisions

- **D1. Retain one builder-created public `PipelineContext`.** Its only public data capability is
  the existing `.computation_graph` property. Arbitrary public construction is forbidden. The sole
  builders pass a validated `InstanceGraph` and canonical selection to a package-private factory.
  The context stores only immutable canonical instance bytes, the canonical selection, and an
  immutable projection receipt. Reading `.computation_graph` verifies the receipt and returns a
  fresh projection. No `InstanceGraph` child or persistent mutable `ComputationGraph` is exposed.
  *Rejected: a public two-graph constructor, because callers can create or mutate a mismatched pair;
  returning only `ComputationGraph`, because it breaks the supported result shape.*
- **D2. Keep the canonical live builder name and supported selection/filter inputs.** Final form is
  `build_pipeline_context(model_paths, targets=None, include_all=True,
  design_path_filter="") -> PipelineContext`. Delete `lower_constraints_enabled`; it exists only to
  admit non-certifying v5 semantics. Targets are resolved at the projection display boundary, then
  exact graph edges compute the dependency closure. Constraints and their dependencies remain roots.
  *Rejected: preserve the lowering flag (creates an uncertifiable authority); delete target/filter
  behavior (breaks supported consumers without semantic cause).*
- **D3. Give live, capture, and freshness one source-admission owner.** A private staged admission
  function fixes the exact document set and bytes before SysIDE parses. Live and capture then call
  one `load_and_elaborate(admission, design_path_filter) -> InstanceGraph`; freshness calls the same
  admission function and compares its manifest. Both public context builders call the same
  projector. Capture calls admission and elaboration once. *Rejected: hash files after SysIDE has
  parsed them, because the parsed semantics and claimed bytes can race; promoting
  `build_elaborated_pipeline`, because it preserves a second authority.*
- **D4. Preserve only import capabilities that exist today.** `sysml_codegen.orchestration` owns
  `build_pipeline_context` and `build_pipeline_context_from_snapshot`.
  `sysml_codegen.generation` and `sysml_codegen.generation.initialization` retain only their current
  aliases for `PipelineContext`, `CodeGenerationError`, and `SysMLParsingError`; neither gains a
  builder alias. The package root remains without these exports. Snapshot re-exports are reduced to
  v6 capture, low-level load, the format constant, and v6 exceptions; the snapshot context builder
  remains orchestration-owned.
  *Rejected: duplicate wrappers under each package (multiple owners); delete harmless aliases
  immediately (consumer breakage unrelated to legacy semantics).*
- **D5. Use one exact v6 envelope digest plus the graph codec's inner digest.** The outer digest
  covers every field except its own value. The inner digest remains defense in depth and keeps the
  codec independently testable. *Rejected: unsigned outer provenance and options (tamper can change
  certification claims); a keyed signature (no trust/key requirement exists).*
- **D6. Treat source verification as an exact admission replay.** Every envelope carries ordered
  roots and hashes for the staged user documents SysIDE actually parsed, plus a hash of the SysIDE
  standard-library environment. When `source_roots` is supplied, the loader reruns the same
  admission algorithm and requires exact root and document-set equality. With no roots, the
  self-contained snapshot is certifiable but freshness is `unverified`. *Rejected: filesystem
  globbing, absolute paths, nearby-tree discovery, and treating the standard library as user input.*
- **D7. Capture is strict and atomic.** It elaborates in strict mode, requires graph validation and
  projectability, constructs and validates the complete envelope in memory, writes a sibling
  temporary file, `fsync`s, then replaces the destination. Failure leaves a pre-existing destination
  unchanged and leaves no new artifact. *Rejected: persist diagnostic graphs (turns refusals into
  loader input); stream directly to the destination (partial artifacts on failure).*
- **D8. V6 has no v5 upgrader, carve-out, or exception alias.** Any absent, v5, or future version
  fails with a recapture message before payload interpretation. All v5 fixtures are removed in the
  accepted recapture. *Rejected: upgrade extracted names into exact identities (reconstructs the
  deleted authority and cannot prove identity).*
- **D9. Move only route-neutral helpers.** Portable source referents move to
  `snapshot/source_manifest.py`; modeled scalar default decoding moves to
  `elaboration/value_defaults.py`; constraint ID rendering moves to
  `generation/constraint_catalog.py`. Exact ownership replaces imports from legacy modules.
  *Rejected: retain a legacy module as a helper bag (its old authority remains importable).*
- **D10. Converge all four Item-6 duals unconditionally.** The final unsuffixed agentic APIs are
  `extract_constraint_facts(model) -> IdentifiedConstraintFacts` and
  `evaluate_profile(facts: IdentifiedConstraintFacts) -> IdentifiedProfileResult`. Delete
  `extract_identified_constraint_facts`, `evaluate_identified_profile`, the QN candidate selector,
  and its export. Validation levels 4 and 6 use the exact result's `item.decision`; `preflight`
  accepts an already-decided exact result and cannot associate candidates. The final unsuffixed
  compiler is the exact ID-keyed core. Calculation payloads are declaration-ID keyed, with names
  only as metadata. *Rejected: validation-only QN association and coexistence assertions, because
  both leave a callable second authority.*
- **D11. Rename the maintained Fusion Tea fixture in place.** Formal names gain an unambiguous
  `_in` suffix while each bare RHS remains the original intended source. Definition equations change
  identifiers only. Module and schema class names remain stable; generated input field names change
  with the formals; public source entry-point keys remain source-QN based. *Rejected: a corrected
  sibling fixture (creates a 38th row); qualified RHS escapes (do not prove D-5).*
- **D12. Promote one content-addressed paired candidate through one coordinator.** The sole command
  is `scripts/check_cutover_candidate.py`; the sole identity is one
  `elaborator-cutover-candidate/v1` record and candidate ID spanning both repositories. Detached,
  clean candidate worktrees become hidden prepared refs without advancing public branches. Two
  owner-created annotated acceptance tags cite the same ID on the authoritative GitHub origins. The
  promotion App prepares, verifies, remotely compare-and-swap promotes/recovers both public refs,
  stages and remotely publishes paired product tags, then gates release.
  *Rejected: independent repository checkers or ordinary merges, because neither can recover or
  hard-block a transient one-sided ref update.*

## Architecture

```text
live paths ──> SysIDE load ──> strict elaborate ──> validated InstanceGraph
                                                     │           │
snapshot capture <── v6 envelope encode <────────────┘           │ sole authority
                                                                 v
v6 snapshot ──> ordered validation ──> decoded InstanceGraph ──> project/select
                                                                 │
                                                                 v
                                                        ComputationGraph ──> generation/seal
```

### Public result and builders

The final public surface is deliberately small:

```python
class PipelineContext:
    @property
    def computation_graph(self) -> ComputationGraph: ...

build_pipeline_context(model_paths, targets=None, include_all=True,
                       design_path_filter="") -> PipelineContext
build_pipeline_context_from_snapshot(snapshot_path, targets=None, include_all=True,
                                     *, source_roots: Sequence[Path] | None = None)
                                     -> PipelineContext
```

`PipelineContext.__new__` and `__init__` reject every public call with
`TypeError("PipelineContext is builder-created; use build_pipeline_context or "
"build_pipeline_context_from_snapshot")`. There is no public factory, pair constructor,
deserializer, mutation method, dataclass replacement path, or pickle reducer. The two public
builders alone call package-private `_make_pipeline_context` after source/envelope validation,
`InstanceGraph.validate()`, `require_projectable()`, and canonical selection.

`source_roots` is exactly `collections.abc.Sequence[pathlib.Path] | None`. A string, bytes object,
non-`Path` member, set, generator, or mapping is a `TypeError`; an empty sequence is a
`SnapshotStaleSourceError`. `None` means the explicit `unverified` freshness state. Root ordering is
semantic and is preserved exactly.

The object is frozen and slotted. Its private state is exactly:

- `_instance_bytes: bytes`: canonical `instance-graph/v2` bytes. This is the authority and is
  immutable.
- `_selection: _Selection`: a frozen record containing a sorted, duplicate-free target tuple and
  `include_all: bool`.
- `_receipt: _ProjectionReceipt`: a frozen record containing
  `instance_fingerprint`, `targets`, `include_all`,
  `projector_semantic_marker="instance-projector/v1"`, and `computation_digest`.

The final public properties are only `.computation_graph` and ordinary object identity/representation
behavior. There is no public `.instance_graph`, `.selection`, or `.receipt`. This is the smallest
shape that preserves the existing consumer capability without exposing a mutable semantic graph.
The property decodes `_instance_bytes` into a fresh graph, checks its fingerprint, validates and
requires projectability, reprojects with `_selection`, recomputes the complete computation digest,
compares all receipt fields, and returns a fresh deep graph. A caller can mutate that returned
Pydantic graph, but the next property access redecodes and reprojects from immutable bytes, so the
mutation cannot persist or disagree with the authority.

The computation digest is SHA-256 over canonical JSON containing the projector marker and every
semantic `ComputationGraph` field: full module records, entry-point groups, execution order,
`fallback_entry_points`, output aliases, and the complete constraint catalog. It includes fields
currently excluded from Pydantic serialization. Arrays retain semantic order; sets are sorted; maps
have sorted keys; non-finite values fail. A receipt test changes each instance byte, selection field,
marker, computation field, excluded field, and digest in turn and requires refusal.

Every certifying generation boundary obtains a package-private verified projection lease from the
context. The lease repeats receipt verification immediately before generation and immediately before
package sealing. The public CLI/package writer never accepts a naked `ComputationGraph`. Pure
render helpers may continue to accept one, but are non-certifying and cannot write or seal a package.
Generation code obtains one graph from the lease and passes that graph to downstream helpers; it
never rereads the property midway. Direct constructor, `object.__setattr__`, shallow/deep copy,
pickle, mutated-view, and stale-receipt tests prove the post-construction defense.

`project(graph, targets=None, include_all=True)` first validates the exact graph. With
`include_all=True`, it projects every eligible node. With `include_all=False`, it renders the
public output index once, requires each named target to resolve exactly once, adds every admitted
constraint as a root, and follows only typed producer/node edges to a closed subgraph. Selection may
use rendered names to identify the requested public output; it may not infer an edge or identity
from a string. Canonical selection treats `targets=None` as `()`, accepts only nonempty strings,
sorts and deduplicates them, and always binds the tuple even when `include_all=True`.

### One staged document-admission algorithm

`snapshot/source_manifest.py::admit_sources` is the sole live, capture, and freshness admission
algorithm. It returns an immutable `SourceAdmission` containing staged file paths, logical
referents, caller-display paths, root records, byte hashes, and the standard-library digest. The
algorithm is fixed:

1. Require a nonempty ordered sequence of file or directory roots. Retain each caller-visible
   lexical absolute path for `design_path_filter`, then resolve the root once with `strict=True`.
   Root symlinks are supported. Duplicate and overlapping roots are supported and keep their
   ordinals. A file root must be a regular lower-case `.sysml` or `.kerml` file.
2. Enumerate resolved directories with sorted `scandir`. Admit only regular lower-case `.sysml` and
   `.kerml` files. Do not follow descendant directory symlinks. Reject a descendant file symlink,
   dangling link, or physical escape. On a case-insensitive platform, reject two paths with one
   `normcase` key; NFC-normalize every logical segment and reject NFC collisions on every platform.
3. Deduplicate one physical file reached through overlapping roots by `(device,inode)`. Assign its
   owner deterministically: an exact file root wins; otherwise the deepest containing directory
   wins; a tie uses the lowest ordinal. Duplicate roots may own no file. The logical referent is
   `root-N/<strict-percent-encoded-relative-path>` and the final set is sorted by referent.
4. Open each resolved file by descriptor. Record `device`, `inode`, size, `mtime_ns`, and `ctime_ns`
   before reading; require UTF-8; hash the exact bytes; copy those bytes to a private mode-0700 stage
   under the logical referent; make the staged file read-only; verify its size and hash. After all
   copies, restat every original and rerun enumeration. Any byte, identity, membership, owner, or
   referent change is `SOURCE_RACE`.
5. Give SysIDE the sorted staged file list, never a staged directory. Hash staged files before and
   after parsing. Require `model.uris(DocumentKind.MODEL)` to equal that list exactly with no
   duplicate, extra, or missing document. Translate source URLs and diagnostics through the staged
   path-to-referent map. Evaluate `design_path_filter` against the retained original display path;
   the filter never changes the admitted document set.
6. `SysideStandardLibraryDigestAdapter` in `snapshot/source_manifest.py` calls SysIDE 0.8.4's
   `Environment.get_default()`, reads each environment document's URL, language, and text, maps the
   URL to a portable name, sorts `(portable-name, language, UTF-8 text)`, and returns the document
   count plus SHA-256. The pinned expected result is 94 documents and
   `ada7a0818f72e95f3953e46592bec91026bbd954efda251decc35d4036272f67`. These documents are the
   standard library, not user files. `import SI::*` adds no `sources.files` row. Imports do not
   discover files: every non-library document must be staged. An unresolved external import is a
   parse refusal; supplying that document as another root is the supported path.
7. Elaborate before deleting the stage. Capture writes hashes for the staged bytes that SysIDE
   parsed. Freshness reruns steps 1–6 and compares root count/order/kind plus the exact sorted
   referent/size/hash set. It detects additions, removals, byte changes, owner changes, and policy
   failures. Without `source_roots`, freshness is explicitly `unverified` and projection remains
   self-contained.

Live/capture admission failures are `SourceAdmissionError`, a `SysMLParsingError` subclass with a
closed code: `SOURCE_ROOT_INVALID`, `SOURCE_ALIAS_COLLISION`, `SOURCE_SYMLINK_ESCAPE`,
`SOURCE_READ_ERROR`, `SOURCE_RACE`, `SOURCE_STAGE_MUTATED`, or `SOURCE_ADMISSION_MISMATCH`.
`SOURCE_STANDARD_LIBRARY_UNAVAILABLE` is the typed admission code when the default environment,
document metadata, or document text is unavailable or unreadable. Live and capture surface it as
`SourceAdmissionError`. Offline v6 compares the stored authority to the pinned count/digest and
uses `SnapshotCompatibilityError` for a mismatch; it never relabels mismatch as admission failure.
SysIDE parse/unresolved-import diagnostics follow admission. Snapshot freshness maps any admission
code or manifest difference to `SnapshotStaleSourceError` carrying that code. Tests cover file and
directory roots, duplicate/overlap ownership, symlinked roots, descendant links, case/NFC
collisions, `.sysml` and `.kerml`, add/remove/change races, exact SysIDE set equality, standard
library separation, external imports, original-path filtering, and staged-byte parsing.

### V6 envelope

This section is the normative v6 schema. `object{...}` means exactly those keys: unknown, missing,
or duplicate keys fail at every depth. `int` excludes Boolean, `number` is finite JSON integer or
float excluding Boolean, `scalar` is finite number/string/Boolean, `wire` is a nonempty canonical
typed-ID wire string, `hash` is 64 lower-case hex characters, and `str` is a JSON string. Arrays
state their cardinality and order. Null is permitted only where written.

| Object | Exact keys and types | Authority |
|---|---|---|
| envelope | `format:"sysml-codegen-instance-graph"`; `version:6`; `authority`; `capture`; `sources`; `instance_graph`; `integrity` | Complete outer authority. |
| authority | `certifiability_profile:"projectable-instance-graph/v1"`; `instance_graph_schema:"instance-graph/v2"`; `expression_ir_schema:"expression-ir/v1"`; `executable_profile:"executable-profile/v4"`; `projector_semantics:"instance-projector/v1"`; `syside_version:"0.8.4"`; `standard_library` | Exact compatibility authority. |
| standard_library | `kind:"syside-default"`; `document_count:int >= 1`; `sha256:hash` | Hash of the parsed environment documents. |
| capture | `model_name:nonempty str`; `captured_at:RFC-3339 UTC str`; `producer`; `options` | Options are semantic. Other fields are integrity-bound provenance. |
| producer | `sysml_codegen_version:nonempty str`; `agentic_mbse_version:nonempty str` | Non-semantic provenance. |
| options | `design_path_filter:str` | Semantic capture option. |
| sources | `roots`; `files`; `fingerprint:hash` | Source identity. |
| root row | `ordinal:int >= 0`; `kind:"file"|"directory"` | Array length >= 1; ordinal equals its zero-based position. |
| file row | `referent:root-N/<canonical percent path>`; `size_bytes:int >= 0`; `sha256:hash` | Array length >= 1; strictly increasing unique referent; suffix `.sysml` or `.kerml`; root ordinal exists. |
| integrity | `algorithm:"sha256"`; `canonicalization:"sysml-codegen-json-v1"`; `digest:hash` | Digest value alone is self-excluded. |

`sources.fingerprint` hashes canonical `{roots,files,capture_options}`. The outer digest hashes the
complete document with only `integrity.digest` omitted. `sysml-codegen-json-v1` is UTF-8 JSON with
sorted object keys, compact separators, ASCII escaping, and non-finite numbers forbidden. JSON
object order and insignificant whitespace are non-semantic; all array orders below are semantic.

`instance_graph` is exact `object{schema_version:"instance-graph/v2", fingerprint:hash, graph}`.
Its fingerprint hashes canonical `{schema_version,graph}`. `graph` is exact
`object{occurrences,attrs,calcs,constraints,diagnostics}`. Public v6 requires `diagnostics:[]` with
cardinality zero. The other arrays are zero-or-more and strictly sorted by `occurrence_id` or
`node_id`, respectively. Duplicate identities fail. Every `source_file` in every attribute,
calculation, and constraint row is a canonical logical referent that equals exactly one
`sources.files[*].referent`; `"unknown"`, an absolute path, a staged path, or an unlisted referent is
invalid.

| Graph record | Exact keys and types |
|---|---|
| occurrence | `occurrence_id:wire`; `parent_id:wire|null`; `containment_slot:wire`; `occurrence_index:int >= 0|null`; `effective_usage_id:wire`; `effective_type_ids:[wire]`; `display_segment:nonempty str`; `package_display:str|null`. Effective type IDs keep most-specific-first semantic order and are unique. |
| scope | `kind:"occurrence"|"package"`; `wire:wire`. |
| attribute | `node_id:wire`; `scope`; `declaration_id:wire`; `slot_id:wire`; `display_path:str`; `display_name:str`; `declaration_qn:str`; `value:scalar|null`; `value_site:"none"|"definition_default"|"specialized_def"|"occurrence_override"`; `alias_target:edge|null`; `is_alias:bool`; `alias_shape:str|null`; `source_file:referent`; `source_line:int >= 0`; `owner_qualified_name:str`. |
| calculation | `node_id`; `scope`; `declaration_id`; `display_path`; `display_name`; `calc_def_name`; `calc_def_qualified_name`; `inputs`; `outputs`; `unbound_formals:[wire]`; `is_computed:bool`; `expression_ir:expression|null`; `aggregation_reference_ordinals:[int >= 0]`; `compilability:"fully_compilable"|"partially_compilable"|"manual_required"`; `auto_impl_context:auto|null`; `doc_comment:str|null`; `calc_expressions:[str]`; `calculation_definition_id:wire|null`; `compilation_definition_id:wire|null`; `compiled_output_ids:[wire]`; `source_file:referent`; `source_line:int >= 0`. ID lists are unique in model order; aggregation ordinals are strictly increasing. `unknown` is never certifiable. |
| constraint | `node_id`; `scope`; `declaration_id`; `display_path`; `display_name`; `constraint_def_name`; `inputs`; `unbound_formals:[wire]`; `predicate_ir:expression|null`; `source_form:nonempty str`; `owner_kind:nonempty str`; `owner_qualified_name:str`; `usage_qualified_name:str`; `membership_kind:str|null`; `predicate_source_key:str`; `is_negated:bool`; `definition_qualified_name:str|null`; `eligibility:"admit"|"block"|"non_numerical"|"unassessed"`; `effective_definition_id:wire|null`; `exclusion_reasons:[str]`; `exclusion_location:str|null`; `source_file:referent`; `source_line:int >= 0`. Public projectability further requires the existing profile consistency rules. |
| input row | `port`; `edge:edge|null`; `name:str`; `metadata`. Sorted strictly by canonical port bytes and unique. |
| consumer port | `kind:"consumer"`; `consumer:wire`; `formal:wire`. |
| expression port | `kind:"expression"`; `consumer:wire`; `reference_ordinal:int >= 0`; `edge_ordinal:int >= 0`; `referenced_declaration:wire`; `target_occurrence:wire|null`. |
| edge | node: `kind:"node",target:wire`; producer: `kind:"producer",target:{calculation:wire,output:wire}`; literal: `kind:"literal",value:scalar`. |
| metadata | `python_type:str`; `description:str|null`; `default_value:scalar|null`; `unit:str|null`; `qualified_name:str|null`; `unresolved_default_kind:str|null`; `formal_provenance:{declaration_id:wire,raw_name:nonempty str,qualified_name:nonempty str}|null`. |
| output row | `declaration:wire`; `port:{calculation:wire,output:wire}`; `name:str`; `metadata`. Strictly sorted by declaration and unique. |
| auto | `execution_steps:[{name:str,expression:str}]`; `output_expressions:[{name:str,expression:str}]`; `output_count:int >= 0`; `single_output_expression:str|null`. Both arrays preserve compiler order and `output_count` equals the second length. |

Every expression node has `schema_version:"expression-ir/v1"` and one exact variant shape:

- literal: `{schema_version,kind:"literal",literal,operand_type}` where literal is exact
  `{kind:str,value:scalar,result_type:str|null}`;
- feature reference: `{schema_version,kind:"feature_ref",reference,operand_type}` where reference
  is exact `{source_name:str|null,target:identity|null,target_types:[str],chain_segments:[str]}` and
  identity is exact `{kind:str|null,name:str|null,qualified_name:str|null}`;
- operator: `{schema_version,kind:"operator",operator:str,operands:[expression],operand_type}`;
- unit: `{schema_version,kind:"unit",value:expression,unit_text:str|null,operand_type}`;
- invocation: `{schema_version,kind:"invocation",function_qn:[str]|null,arguments:[expression],operand_type}`;
- unsupported: `{schema_version,kind:"unsupported",node_kind:str,diagnostic:str,source_text:str|null}`.

`operand_type` is null or exact `{category,enumeration,unit}`. Category is
`"boolean"|"string"|"integer"|"real"|"enum"|"quantity"|"unresolved"|"unknown"`;
`enumeration` is string/null; `unit` is null or exact `{unit:str|null,dimension:str|null}`. Child
arrays preserve authored expression order. The v6 validator checks these exact shapes before the
agentic decoder, which currently ignores extras.

`projectable-instance-graph/v1` covers outer-envelope rules and failure order, source admission and
freshness, standard-library binding, graph decode/validation/projectability, canonical selection,
target ambiguity and exact-edge closure, projection/render/collision semantics, computation digest,
and receipt lifetime verification. A persisted key/type/cardinality/order/digest-coverage change
requires a new snapshot format version. A graph-wire or expression/profile wire change also bumps
its own marker. A semantic change to admission, projectability, selection, projection, computation
digest, or receipt verification bumps the certifiability profile; projection output semantics also
bump `projector_semantics`. A pure refactor, performance improvement, log wording change, or
provenance value change does not bump. Loaders exact-match markers; there is no compatible range.

### Validation and failure order

Validation order is observable and fixed. A payload that violates several layers reports the first
layer below, so stale or incompatible bytes never reach projection.

1. Read bytes; parse JSON with duplicate-key detection; require a top-level object. Syntax, duplicate,
   and I/O shape failures raise `SnapshotFormatError`.
2. Read only `version`. Missing, non-integer, v5, and future versions raise `SnapshotFormatError`
   with “recapture with snapshot v6”; no v5 field is inspected.
3. Validate the exact top-level and nested shape, canonicalize the document, and verify the outer
   digest. Shape failures raise `SnapshotFormatError`; digest failure raises
   `SnapshotIntegrityError`.
4. Exact-match `format`, certifiability profile, graph/IR/profile/projector markers, SysIDE pin, and
   standard-library authority. A mismatch raises `SnapshotCompatibilityError` before graph decode.
5. Validate source ordinals, referents, ordering, sizes/hashes, and source fingerprint. Internal
   inconsistency raises `SnapshotIntegrityError`. Before typed graph construction, scan every raw
   graph `source_file` and require exact membership in `sources.files`; a missing or extra referent
   is `SnapshotIntegrityError`. If `source_roots` was supplied, run the shared staged admission
   algorithm and compare exact roots and admitted set. Any admission code, addition, removal, owner
   change, or byte difference raises `SnapshotStaleSourceError` before graph decode. No roots records
   `unverified`; it is not a freshness pass.
6. Verify the inner graph schema/fingerprint and decode every typed ID, record, IR node, and edge.
   Inner digest failure maps to `SnapshotIntegrityError`; invalid graph payload maps to
   `SnapshotFormatError`.
7. Run `InstanceGraph.validate()` and require empty diagnostics/projectability. Failure raises
   `SnapshotCertifiabilityError`. A public v6 file can never carry a diagnostic outcome.
8. Resolve targets and project. Ambiguous/missing requested targets raise `CodeGenerationError`;
   an identity-losing render raises `ProjectionError`.

All snapshot exceptions derive from `SnapshotFormatError` so existing callers may keep one broad
catch while tests can assert precise failure. `GrandfatheredSnapshotError` and its assertion helper
are deleted, not aliased. Live load continues to raise `SysMLParsingError`; authored blocking forms
raise `ElaborationDiagnosticError`; violated exact invariants raise `ElaborationInvariantError`;
missing calculation definitions and invalid target selection raise `CodeGenerationError`; render
collisions raise `ProjectionError`. Capture additionally exposes `OSError` for the final filesystem
operation. The CLI catches these named failures, logs one error, returns exit code 1, and writes no
new output; success remains 0.

### Capture and relocation

`capture_snapshot(model_paths, output_path, design_path_filter="") -> Path` retains its signature
and overwrite behavior. It always captures the full instance graph; target selection is a generation
concern. It admits and stages once, makes SysIDE parse those exact hashed bytes, elaborates once,
constructs the envelope in memory, round-trips it through the public validator, writes and `fsync`s
one sibling temporary file, then atomically replaces `output_path`. The return is the exact
destination `Path`. Any failure leaves an existing destination byte-identical and removes the exact
temporary file.

Relocation changes neither the stored bytes nor graph semantics. A moved envelope loads without its
sources. A caller that wants freshness validation passes an ordered replacement `source_roots`
sequence; `root-N` then maps to the corresponding new root. The snapshot's own directory never
participates in identity. In-place and relocated routes must produce the same graph fingerprint,
projected semantic digest, generated package bytes after normalized provenance, and mutation result.

## Required Invariants

- **I1.** Every public generation route obtains semantics from exactly one validated `InstanceGraph`.
- **I2.** No production module outside exact elaboration creates a semantic edge, occurrence, value
  source, or constraint decision from a qualified name or rendered path.
- **I3.** `ComputationGraph` is downstream-only. No loader, elaborator, snapshot encoder, or selector
  uses it to reconstruct instance semantics.
- **I4.** Live and v6 paths call the same projector with the same selection arguments.
- **I4a.** A `PipelineContext` can be created only by the two builders. Its authority is immutable
  canonical bytes; every derived graph view is fresh; every certifying generation boundary verifies
  the bound receipt before generation and before sealing.
- **I5.** Capture cannot write a graph with diagnostics, failed validation, incompatible pins, or an
  unresolved projection collision.
- **I6.** The v6 outer digest binds every field except itself; the source and graph nested digests are
  independently recomputed.
- **I6a.** SysIDE parses the exact staged bytes named by the source manifest, and its user document
  set equals the admitted set. The standard library is separately hashed compatibility authority.
- **I7.** No v5 payload is decoded or upgraded. No stale v5 fixture remains outside historical
  `.project/` records.
- **I8.** `targets`, `include_all`, and `design_path_filter` preserve supported behavior without
  reintroducing legacy identity. Snapshot generation still rejects a new design-path filter.
- **I9.** A runtime-source mutation changes every and only the exact consumer ports bound to that
  source, on live, in-place-v6, and relocated-v6 routes.
- **I10.** Every deleted responsibility has one independent replacement oracle and a static residue
  gate in the census.
- **I11.** The maintained corpus contains exactly 37 paths. Only runtime-source rows produce v6
  files; refusal and load-error rows do not.
- **I12.** No final commit or merge exists in which both public authorities survive or the accepted
  v6 corpus is paired with the old authority. The landed bytes must reconstruct the owner-accepted
  paired candidate ID exactly.

## Component Overview

| Component | Final owner | Responsibility |
|---|---|---|
| Live orchestration | `orchestration/pipeline_builder.py` | Public load/elaborate/project builder; no legacy stages. |
| Public result | `orchestration/pipeline_context.py` | Builder-created immutable instance bytes, canonical selection, receipt, and defensive derived view. |
| Exact model semantics | `elaboration/{identity,occurrence,elaborate,graph}.py` | Exact IDs, effective occurrences, typed payloads/edges, diagnostics, validation. |
| Projection and selection | `elaboration/project.py` | Exact-edge subset closure and one-way rendering to `ComputationGraph`. |
| V6 envelope | `snapshot/{envelope,source_manifest,capture}.py` | Canonical encode/decode, integrity, source checks, strict atomic capture. |
| Offline orchestration | `orchestration/snapshot_context.py` | V6 load then the shared projector; no rebuild. |
| Generation seam | `resolution/models.py`, `generation/*` | Consume one receipt-verified projection lease; pure helpers receive the derived graph. |
| Agentic exact facts/profile/IR | `../agentic-mbse/src/agentic_mbse/sysml/*` | One identified fact pass, exact profile decision, exact compiler/IR core. |
| Acceptance evidence | Item-7 acceptance tests and one temporary measurement driver | Route parity, budgets, real TEAx, accepted manifest, and residue checks. |

## Fusion Tea Migration and Generated Consequences

Every occurrence binding becomes `in <formal>_in = <original bare source>`. The matching formal
declaration and every expression reference change in place. These are the exact fifteen obligations:

| ID | Definition / occurrence | Old binding | Final binding |
|---|---|---|---|
| `FT-01` | `IFE LCOE` / `lcoe_calc` | `availability = availability` | `availability_in = availability` |
| `FT-02` | same | `discount_rate = discount_rate` | `discount_rate_in = discount_rate` |
| `FT-03` | same | `frequency = frequency` | `frequency_in = frequency` |
| `FT-04` | same | `gain = gain` | `gain_in = gain` |
| `FT-05` | same | `om_cost_constant = om_cost_constant` | `om_cost_constant_in = om_cost_constant` |
| `FT-06` | same | `plant_cost_constant = plant_cost_constant` | `plant_cost_constant_in = plant_cost_constant` |
| `FT-07` | same | `thermal_efficiency = thermal_efficiency` | `thermal_efficiency_in = thermal_efficiency` |
| `FT-08` | `Recirculating Power Fraction` / `recirc_calc` | `gain = gain` | `gain_in = gain` |
| `FT-09` | same | `thermal_efficiency = thermal_efficiency` | `thermal_efficiency_in = thermal_efficiency` |
| `FT-10` | `Viability Threshold` / `viability` | `gain = gain` | `gain_in = gain` |
| `FT-11` | `Meier Reactor Cost` / `meier_reactor_cost_calc` | `thermal_power_gw = thermal_power_gw` | `thermal_power_gw_in = thermal_power_gw` |
| `FT-12` | `Meier COE` / `meier_coe_calc` | `availability = availability` | `availability_in = availability` |
| `FT-13` | same | `net_electric_power_gw = net_electric_power_gw` | `net_electric_power_gw_in = net_electric_power_gw` |
| `FT-14` | `Meier HIF Driver Cost` / `meier_cost` | `beam_energy_mj = beam_energy_mj` | `beam_energy_mj_in = beam_energy_mj` |
| `FT-15` | same | `num_chambers = num_chambers` | `num_chambers_in = num_chambers` |

The maintained SysML files and generated consequences are enumerated under `FIX-01.*` in the
census. Module paths, schema class names, outputs, public source keys, defaults, and physics stay
fixed. Formal-derived input fields change. The compiler goldens change only at the affected records:

- `calc_def_compilation_golden.json`: 15 output records. IFE LCOE changes
  `discount_factor_con`, `discount_factor_op`, `fusion_energy_per_shot`, `net_electric_power`,
  `annual_capital_cost`, `annual_energy`, `pvf_construction`, `pvf_operation`, `shots_per_year`, and
  `annual_operating_cost`; Meier COE changes `coe_cents_kwh`; Meier HIF Driver Cost changes
  `bank_energy_joules` and `cost_billions`; Meier Reactor Cost changes `reactor_cost_billions`;
  Recirculating Power Fraction changes `fusion_cycle_gain`.
- `calc_compat_parity_golden.json`: exactly three direct records change: Meier COE
  `coe_cents_kwh`, Meier HIF Driver Cost `cost_billions`, and Meier Reactor Cost
  `reactor_cost_billions`. IFE LCOE `lcoe`, driver `gamma`, and recirculating `f_recirc` remain
  independent arithmetic controls.
- Direct generated calls change only
  `beam_energy_mj`/`num_chambers` to `_in` and `gain`/`thermal_efficiency` to `_in` in
  `tests/runtime/test_fusion_tea_acceptance.py`. Generated full-pipeline mapping assertions change
  through the exact fifteen fields, not by normalizing both sides.

The public C25 proof requires one `hif_plant.availability` entry point and exactly the
`lcoe_calc.availability_in` and `meier_coe_calc.availability_in` consumer ports. Mutating it alone
must change only those two consumers; a negative set enumerates every other input and output as
unchanged. The public C2 proof requires one
`hif_plant.thermal_efficiency` entry point and exactly the
`lcoe_calc.thermal_efficiency_in` and `recirc_calc.thermal_efficiency_in` ports, with an independently
enumerated negative set. C19 separately requires literal `80.0` at its exact calculation and
constraint consumer IDs. Its arithmetic assertion and the structural absence of supplied-value
machinery are separate tests. Real TEAx execution is a fourth proof and cannot substitute for any
of these static or mutation oracles.

## Closed Deletion and Migration Sequence

1. **Converge agentic-mbse internals while keeping them nonparallel.** Make the identified constraint
   record the single unsuffixed extraction product. Make `evaluate_profile` the exact identified
   evaluator. Migrate validation levels 4 and 6 and preflight to the exact result, then delete the QN
   candidate selector, transitional identified names, exports, tests, and name-keyed AST walk. A
   remaining display formatter must have a distinct `format_*` name, accept already-decided exact
   result data, and return text only. Calc payload maps become ID-keyed; names remain metadata.
2. **Prepare exact downstream owners without exporting a second route.** Move the three neutral
   helpers, complete target selection in projection, build v6 envelope/source validation, and make
   the builder-created receipt-bound context. These commits are explicitly incomplete and cannot be
   released.
3. **Migrate every caller and test to the canonical builders.** Generation, scripts, public route
   tests, the 29 cells, C19/C2/C25, and real execution use only live/capture/v6 load APIs.
4. **Delete the old authority in the same cutover commit.** Remove the legacy builder body,
   occurrence/path reconstruction, VBR and self-binding rescue, aggregation re-derivation, virtual
   usage expansion, semantic backtracking, key-table resolution, supplied-value materialization,
   OutputRegistry, legacy graph assembly, v5 serializer/loader/rebuild, parallel exact wrapper,
   dual-run diff/runner, and all old exports and mechanism tests. Prune legacy-only extraction data
   models after callers move.
5. **Create one immutable candidate corpus batch.** Run the exact 37-path manifest. Runtime rows get v6;
   diagnostic/load rows get recorded typed outcomes and no file. Normalize `captured_at` for review,
   classify every semantic diff against the accepted Item-5 ledger, remove every v5 file, and build
   the canonical paired candidate record described below.
6. **Run acceptance and request the owner checkpoint.** Do not commit the candidate recapture as
   authority until the owner records accept. A revise result replaces the temporary candidate; it
   does not add another ledger or committed batch.
7. **Promote only the accepted singular candidate ID.** One record binds the codegen and agentic
   prepared commits, accepted snapshots, manifest, fixture renames, deletions, tests, census, and
   evidence. The coordinator proves both public refs reconstruct the two bound content roots and
   patches. Neither repository can pass tag or release gates alone.

The exact files, exports, callers, scripts, tests, replacement IDs, and residue gates for this
sequence are closed in [cutover-census.md](cutover-census.md).

## Non-Goals

- Item 8's committed generated Fusion Tea/Stellarator packages, downstream studies, July IFE impact
  work, certification repair, modeling guidance, and architecture documentation.
- A general snapshot migration framework or v5 compatibility period.
- A new name-resolution, graph, compiler, registry, or persistence abstraction beside the certified
  exact components.
- TEAx production or test changes. Item 7 treats a pinned real TEAx install/checkout as evidence only.
- Changing Fusion Tea physics, source attributes/defaults, calculation outputs, module identities, or
  the 37-path population.
- Turning test-only diagnostic graphs into public artifacts.

## Implementation Notes

- Preserve the dirty Item-6 worktrees. Build on them; never reset or recreate certified files.
- Use a JSON loader with duplicate-pair rejection. `dict` construction after ordinary `json.loads`
  is too late to detect duplicate keys.
- Validate a complete in-memory envelope by the public decoder before opening the temporary output.
  Use an explicit sibling temp path and `os.replace`; cleanup only that exact temp path.
- Source enumeration must come from documents actually admitted by SysIDE, not a filesystem glob.
  A source added to a directory but not loaded cannot silently alter the manifest.
- Exact-edge target closure belongs in projection. Do not copy the dependency backtracker and do not
  parse channel names back into producers.
- Generation logging must count `instance_graph.calcs`, not resurrect `ctx.calc_defs`.
- Historical `.project/` references are excluded from no-residue scans. Production, tests, scripts,
  templates, package metadata, and docs are included.
- The final accepted manifest records actual outputs and counts. Design-time expected outcomes in the
  census are gates, not permission to overwrite an unexpected result.

## Potential Risks

- **A useful legacy oracle is mistaken for a mechanism test.** Mitigation: responsibility-level test
  rows map each deletion to one independent replacement; the matrix cannot blanket-replace suites.
- **Envelope integrity appears stronger than it is.** SHA-256 here detects corruption and unreviewed
  mutation; it is not authentication. The design deliberately does not call it a trust signature.
- **Target selection regresses because old backtracking mixed discovery and pruning.** Mitigation:
  focused all-vs-target closure tests use independent expected node sets and mandatory constraint
  roots on all three routes.
- **Formal renames change generated API call sites.** Mitigation: the exact rename table and census
  make each call/test owner explicit; module/schema/output identities stay fixed.
- **A paired-repository change lands one-sided.** Mitigation: the sole coordinator promotes both
  compare-and-swap refs under one lock, rolls back the first on a second-ref failure, and hard-blocks
  tags/releases if rollback cannot restore the pair.
- **Budget evidence hides nondeterminism.** Mitigation: one warm-up plus three runs records exact
  occurrence/node/edge/envelope counts and semantic digests, all of which must match.

## Integration Strategy

Internal phases are permitted, but “complete” has one meaning: one public live builder, one strict
capture function, one v6 loader/builder, one projector, no deleted owner or compatibility surface,
and one owner-accepted corpus batch. Until the last changeset passes that gate, the branch is an
incomplete migration and must not merge or release. This avoids pretending Git can make two
repositories transactional while still enforcing an atomic product state.

Public CLI behavior remains stable: `generate` requires exactly one of `--models` or
`--from-snapshot`; keeps output, package, schema, pipeline, overwrite, preserve, smart-regeneration,
verbose, and live filter options; rejects filter plus snapshot; returns 0/1; and never clears output
before all semantic and name preflights pass. `snapshot` keeps models, optional output/default path,
filter, verbose, return code, and overwrite-on-success behavior. Python target/include selection is
available on both live and snapshot builders even though the CLI does not currently expose flags.

### Immutable paired candidate

The promotion unit is one canonical file,
`.project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json`, with schema
`elaborator-cutover-candidate/v1`. It has one ID for both repositories. Its exact top-level keys are
`schema`, `candidate_id`, `self`, `repositories`, `bound_paths`, `accepted_batch`, `contracts`,
`commands`, `results`, `evidence_templates`, `environment`, `teax`, and `promotion`.

The ID payload is self-reference safe. Canonical JSON uses sorted keys, compact separators, ASCII,
and finite values. `candidate_id` is omitted. The candidate record's own sole path row is replaced
by exact sentinel `{repo:"sysml-codegen",path:".project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json",canonicalization:"candidate-self-excluded/v1"}`.
No other byte or field is excluded. The persisted file must itself be canonical and contain
`candidate_id = sha256(canonical payload)`.

Evidence that carries the ID uses a computable preimage. Each schema-declared JSON evidence
template contains exact sentinel `__ELABORATOR_CUTOVER_CANDIDATE_ID__` at every candidate-ID slot.
`evidence_templates` is sorted by path and binds the evidence schema, template SHA-256, and the
complete sorted RFC-6901 JSON-pointer list for those slots. Its `bound_paths` row uses
`hash_kind:"evidence-template"` and that template hash. Raw evidence uses `hash_kind:"raw"` and
its final-byte hash.

After computing the ID, materialization replaces only the declared sentinels with that ID.
Verification parses the materialized JSON, requires the ID at every pointer, rejects the ID at an
undeclared location, substitutes the sentinel back, canonicalizes, and requires the template hash.
The materialized byte hash is journal evidence, not an ID input. The candidate-record self sentinel
and declared evidence-template substitution are the only non-raw hashing rules.

`repositories` has exactly `sysml-codegen` and `agentic-mbse`. Their authoritative origins are
`https://github.com/1cFE/sysml-codegen.git` and
`https://github.com/1cFE/agentic-mbse.git`, respectively. Each binds that exact origin, base
commit/tree, public target ref, full candidate content root, normalized base-to-candidate patch
digest, hidden prepared-ref grammar, acceptance-tag grammar, and release-tag ref. `bound_paths` is a
complete sorted inventory of every tracked candidate path in both repositories with mode, size, and
SHA-256. The self row uses only the sentinel above. Candidate content roots hash those complete
inventories. Patch digests hash canonical changed-path/status/mode/old-hash/new-hash rows; the self
row again uses the same sentinel. Git commit IDs are intentionally journal state, not ID input,
because the record is inside the codegen tree.

Local repositories and worktrees are preparation inputs only. Base commits, public branches,
acceptance tags, and product tags are authoritative only when freshly read from those two origins.

`accepted_batch` binds every v6 byte, refusal record, 37-path manifest row, normalized review diff,
and owner-review rendering. `contracts` binds the spec, both reviews, design, census,
`cutover-inventory/v1`, candidate schema, v6, graph, expression, profile, projector, and
certifiability versions. `commands` contains exact argv, cwd, and relevant environment for every
quality, inventory, residue, capture, scale, license, and TEAx command. `results` binds exit status,
stdout/stderr hashes, collected/passed/failed/skipped/xfailed/deselected counts, timings, and all
raw or evidence-template result descriptors; it never binds a materialized ID-bearing final-byte
hash. `environment` binds OS, Python, uv, SysIDE, pytest, Ruff, and mypy state. `teax`
binds real path, remote, commit/tree, dirty-patch digest, distribution/version, lockfile, interpreter,
and execution results. Any bound byte, ref name, base, content root, patch, command, result,
environment, TEAx state, census, inventory, or schema change requires a new ID and new acceptance.

#### Prepared refs and acceptance

Candidate work is committed in clean detached worktrees at
`/home/reid/1cfe/cutover-prepared/sysml-codegen` and
`/home/reid/1cfe/cutover-prepared/agentic-mbse`. `prepare` creates, with compare-and-swap from a
missing ref, one hidden ref in each repository:
`refs/cutover/elaborator-cutover/<candidate_id>/prepared`. These refs point to local prepared commit
objects and do not advance a public branch. The commit contents must match the record's complete
path inventory, content root, normalized patch, and base. Commit author/time/message may differ
without changing the ID; the journal binds the exact prepared object IDs used for promotion.

After reviewing the bound record and evidence, the owner creates one immutable annotated tag in
each repository at `refs/tags/elaborator-cutover/accepted/<candidate_id>`. Each tag targets that
repository's prepared commit and has canonical annotation keys `schema` with value
`elaborator-cutover-acceptance/v1`, `candidate_id`, `repository`, `disposition:"accepted"`,
`reviewer`, and `reviewed_at`. The owner publishes each tag to its authoritative origin with
compare-and-swap from a missing remote ref. Both remote tags must cite the same ID and reciprocal
repository set. They record review only and never alter a tree or count as a product release tag.
Changing, deleting, or retargeting either remote tag invalidates acceptance.

#### Sole coordinator and phase contract

`scripts/check_cutover_candidate.py` is the only coordinator/checker. Remote mutation runs as the
GitHub App `1cfe-elaborator-cutover-promoter`, whose installation identity is
`1cfe-elaborator-cutover-promoter[bot]`. Its short-lived token is supplied only through
`CUTOVER_PROMOTION_GITHUB_TOKEN`; local user credentials are rejected for mutation phases. Every
phase receives
`--record .project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json`,
`--state-dir /home/reid/1cfe/.cutover/elaborator-cutover`,
`--codegen-repo /home/reid/1cfe/sysml-codegen`, and
`--agentic-repo /home/reid/1cfe/agentic-mbse`. Remote mutation phases additionally require
`--token-env CUTOVER_PROMOTION_GITHUB_TOKEN`. `prepare` additionally requires the two exact
`--codegen-worktree` and `--agentic-worktree` paths above. `verify-release` additionally requires
`--release-manifest .project/active/elaborator-cutover/evidence/release-manifest.json`.

The accepted CLI grammar has no aliases or optional phase inputs: `prepare` is the common four
flags plus `--codegen-worktree /home/reid/1cfe/cutover-prepared/sysml-codegen` and
`--agentic-worktree /home/reid/1cfe/cutover-prepared/agentic-mbse`; `verify`,
and `verify-tags` are exactly the common four; `promote-branches` and `publish-tags` add the token
flag; `recover-hard-block` adds the token flag plus exactly `--scope branches --target bases|candidate`
or `--scope product-tags --target absent|published`; `verify-release` is the common four plus the
release-manifest flag above. Relative repository/state/worktree paths, additional repositories, a
phase list, and a second candidate record are rejected.

- `prepare` requires canonical record bytes and evidence templates; clean detached candidate
  worktrees; exact origins; expected base ancestry; fresh `git ls-remote --refs` results showing
  both authoritative public refs at their bound base OIDs; exact inventories, roots, patches,
  corpus/refusal/diff bytes, commands/results, environment, and TEAx; reciprocal agreement; and no
  foreign local prepared ref. It creates the two hidden local refs and durably writes
  `<state-dir>/<candidate_id>/promotion-journal.json` in `PREPARED` without changing a remote ref.
- `verify` is read-only. It freshly reads both origins, fetches the exact remote objects needed for
  validation, and rechecks the record, templates/materialized evidence, local prepared commits,
  remote public refs, all bound bytes/results, and both authoritative owner acceptance tags. It
  emits a canonical result but changes no ref and no journal state. Any branch or tag hard block is
  a refusal; only `recover-hard-block` can repair it.
- `promote-branches` requires the promotion App, acquires the named lock, refuses a hard-blocked
  journal, reruns read-only verification, and fsyncs `PROMOTING_BRANCHES`. For codegen and then
  agentic it freshly reads the authoritative OID and performs
  `git push --porcelain <origin> <prepared_oid>:<public_ref> --force-with-lease=<public_ref>:<base_oid>`.
  It records the observed expected OID, push result, and fresh returned `ls-remote` OID. If agentic
  fails, it compensates codegen with the inverse remote lease
  `<base_oid>:<public_ref> --force-with-lease=<public_ref>:<prepared_oid>`. Successful compensation
  records `ROLLED_BACK`; failure records `HARD_BLOCKED`. Both successful pushes and post-push remote
  reads record `BRANCHES_PROMOTED`.
- `recover-hard-block` is the only repair mutation. For `--scope branches`, allowed observations
  are only each repository's base or prepared OID. `--target bases` CAS-restores both bases and
  finishes `ROLLED_BACK`; `--target candidate` CAS-advances both prepared OIDs and finishes
  `BRANCHES_PROMOTED`. Intermediate states are `RECOVERING_BRANCHES_BASES` or
  `RECOVERING_BRANCHES_CANDIDATE`. For `--scope product-tags`, allowed observations are only missing
  or the exact staged tag-object OID. `--target absent` removes both with leases and finishes
  `TAGS_ROLLED_BACK`; `--target published` creates both and finishes `TAGS_PUBLISHED`. Intermediate
  states are `RECOVERING_TAGS_ABSENT` or `RECOVERING_TAGS_PUBLISHED`. Each two-update repair uses the
  same order and compensates the first to its observed state if the second fails. Failed
  compensation remains `HARD_BLOCKED` or `TAGS_HARD_BLOCKED`. A foreign/moved OID, wrong candidate,
  absent acceptance, missing App identity, or ambiguous journal refuses without mutation.
- `publish-tags` requires `BRANCHES_PROMOTED`, remote branches still at prepared OIDs, and both
  authoritative acceptance tags. From record-bound tagger identity/time, tag ref names, targets,
  and schema-declared sentinel message templates, it creates the two exact annotated tag objects
  locally with `git mktag` and records `TAGS_STAGED`. Under the lock it publishes codegen then
  agentic by remote missing-ref lease:
  `git push --porcelain <origin> <tag_object_oid>:<tag_ref> --force-with-lease=<tag_ref>:`.
  A second push failure deletes the first with
  `git push --porcelain <origin> :<tag_ref> --force-with-lease=<tag_ref>:<tag_object_oid>`.
  Successful rollback records `TAGS_ROLLED_BACK`; failed rollback records `TAGS_HARD_BLOCKED`; two
  successful pushes plus fresh authoritative reads record `TAGS_PUBLISHED`.
- `verify-tags` is post-publication and read-only. It requires `TAGS_PUBLISHED`, both remote branches
  and acceptance tags exact, and both protected product tag refs present at the staged annotated
  objects, with messages citing the same ID and targets peeling to the prepared commits. Missing,
  one-sided, foreign, or hard-blocked state fails without mutation.
- `verify-release` is read-only. It reruns full candidate and tag verification and requires an exact
  release manifest binding both origin/ref/tag/content-root tuples. Packaging or publication is
  forbidden unless this command succeeds; it does not change refs or clear a block.

The journal is canonical JSON with protocol version, candidate ID, phase, both origins, bases/public
refs, local prepared refs/object IDs, acceptance/product tag object IDs, attempts, every freshly
observed authoritative remote OID, push return, rollback/compensation action, error, and timestamp.
Every transition uses write/fsync/atomic-replace plus parent-dir fsync while the lock is held.
`HARD_BLOCKED` or `TAGS_HARD_BLOCKED` makes branch, tag, and release checks fail until the authorized
recovery command records one of the exact paired terminal states above.

Two Git repositories cannot share one physical ref transaction. The product guarantee is therefore
logical atomic landing: a transient one-sided public-branch update is automatically rolled back or
hard-blocked, and no one-sided state can pass tag or release gates. This does not weaken the spec's
one shipped authority. The accepted paired state is the only taggable and releasable state.

Before `prepare`, both GitHub repositories must install rulesets that protect the record-bound public
branches against direct push, deletion, force update, and ordinary merge; allow only the promotion
App; and require status `elaborator-cutover/candidate`. The acceptance tag namespace is owner-only,
immutable, and excluded from the App's write permission. The product tag namespace is protected so
only the App can publish/delete it. Branch workflows call `promote-branches`; tag workflows call
`publish-tags` then `verify-tags`; release workflows call `verify-release`. Each uses a reciprocal
checkout and fresh authoritative remote reads and fails closed when the peer origin, App token, or
shared state directory is unavailable.

## Validation Approach

### DR3 census-closure evidence

The design-stage checkers are now kept artifacts, not implementation promises:
`scripts/check_cutover_census.py`, `scripts/check_cutover_residue.py`, and their two unit-test files.
On 2026-08-10 the focused tests passed 4/4. The documented inventory command generated
`.project/active/elaborator-cutover/cutover-inventory.json` with 231 closed, sorted rows, including
78 paths discovered by the encoded marker scan. Exact compare passed. The self-safe residue scan
classified 363 current transitional hits under `all` and five under `item6-dual-2`; every hit maps
to an existing `delete` or `migrate` row. These are design-census results. The accepted implementation
candidate must run the same rules with `--expect absent` and get zero.

Both source repositories contain the certified dirty Item-6 prerequisite state. The generated
inventory therefore records `comparison_basis:"current-worktree"` and
`exact_base_comparison:false` for each repository. It binds current HEAD, dirty-state digest, and
each existing row's current bytes. It does not claim a clean-base comparison that the present state
cannot supply. Candidate `prepare` later requires the clean detached worktrees and exact bases in
the promotion protocol.

### Authority and route proofs

- Public import/return tests assert that every public constructor form fails, `.computation_graph`
  is the sole public data property, each access is a fresh verified projection, mutations do not
  persist, and current re-export identities plus deleted snapshot-export absence are exact.
- Live, in-place-v6, and relocated-v6 tests compare the instance graph fingerprint, derived semantic
  graph digest, generated files after allowed provenance normalization, and off-default mutations.
- V6 tests cover every envelope field, duplicate/unknown/missing keys, semantic tamper, provenance and
  option tamper, inner and outer digest failure, every compatibility marker, source manifest skew,
  source-root staleness, field-order-only success, relocation, v5/future rejection, and no upgrader.
- Capture refusal tests precreate no destination and an existing sentinel destination; both prove no
  new/partial artifact and no overwrite on failure.

### Independent semantic proofs

- The inherited 29-cell contract remains authoritative by path.
- One-to-one replacements in the census preserve useful backtracker, resolution, aggregation,
  registry, graph assembly, snapshot, orchestration, runtime, and execution responsibilities without
  executing the old front end.
- C19 proves `80.0` structurally in the exact graph and publicly through separate calc and constraint
  consumers. C25 and C2 prove exact source cardinality, exact consumer sets, and negative unaffected
  sets under distinct mutations.
- `CUT-F26-01` is a dedicated literal oracle over `wi014_toy`: group `toy_plant_params`; source
  keys `toy_plant__demo_plant__plant_budget`, `toy_plant__demo_plant__plant_length`,
  `toy_plant__demo_plant__plant_unit_cost`, and `toy_plant__demo_plant__plant_width`; sole alias
  `("total_cost","toy_plant__demo_plant__cost_calc__cost","demo_plant","part_def",
  "demo_plant__total_cost.json")`; sole constraint ID
  `toy_plant__demo_plant__affordable__c122240f4b148939`. The test imports no old builder. Route
  parity and structural absence remain separate tests.

### Scale and real TEAx evidence

`scripts/measure_item7_acceptance.py` runs one warm-up and three measured Fusion Tea iterations.
Each public capture measurement wraps one stock
`capture_snapshot(model_paths, output_path, design_path_filter="")` call from immediately before the
call until return. It includes admission, SysIDE load, elaboration, envelope work, fsync, and replace
and must be <=5 seconds. Internal load+elaboration (<=10 seconds), projection (<=2), generation and
seal (<=30), and TEAx execution (<=30) are supplemental. `time.perf_counter_ns` is the clock. Peak
RSS is <=512 MiB and the v6 file is <=25 MiB. Counts and semantic digests must match across all three
measured runs and live/in-place/relocated routes.

Evidence binds OS/kernel, CPU, RAM, Python/uv, lock hash, SysIDE license/version, the candidate ID,
and TEAx. The execution environment is `/home/reid/1cfe/teax/.venv/bin/python`; the TEAx checkout is
`/home/reid/1cfe/teax` at clean commit `fa0e06a99b070346e68a3b3c29cfec546f3ac728`. Candidate
creation rechecks and hashes that exact interpreter, checkout, lock, distribution, and dirty state.

Temporary live and relocated packages are generated under a new OS temp directory and auto-sealed.
Both `sysml_codegen.contracts.verify.verify_package(...).ok` and the emitted verifier must accept and
agree on covered hashes before execution. The test imports each generated package's public
`create_<package>_registry`, verifies it is backed by real
`simkit.core.registry_builder.create_registry`, and calls real
`simkit.core.pipeline.execute_pipeline`. Both yield LCOE `270.1211779380445` at relative tolerance
`1e-6`; separate C25 and C2 input mutations prove every-and-only propagation. No stub, private
helper, generated package, or run output is committed.

The stock `uv run pytest tests/` excludes the execution marker. The explicit execution gates are:

```bash
PYTHONPATH=/home/reid/1cfe/sysml-codegen/src:/home/reid/1cfe/agentic-mbse/src \
  /home/reid/1cfe/teax/.venv/bin/python -m pytest -o addopts='' -m execution \
  tests/execution/test_fusion_tea_item7_real_teax.py \
  tests/execution/test_fusion_tea_item7_budget.py --collect-only -q
PYTHONPATH=/home/reid/1cfe/sysml-codegen/src:/home/reid/1cfe/agentic-mbse/src \
  /home/reid/1cfe/teax/.venv/bin/python -m pytest -o addopts='' -m execution \
  tests/execution/test_fusion_tea_item7_real_teax.py \
  tests/execution/test_fusion_tea_item7_budget.py -vv
```

Collection must report exactly two tests. Execution must report two passed, zero skipped, zero
xfailed, and zero deselected. A missing marker, wrong venv, wrong TEAx real path/revision, or dirty
TEAx checkout fails before collection.

### Repository gates

Run these exact repository-local commands:

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest tests/
uv run ruff check src --output-format json
uv run ruff check src tests --output-format json
uv run mypy src --show-error-codes --no-error-summary --no-pretty --hide-error-context
test -n "$SYSIDE_LICENSE_KEY"
env SYSIDE_LICENSE_KEY="$SYSIDE_LICENSE_KEY" uv run pytest -o addopts='' \
  tests/conformance/test_constraint_generation_live.py::test_s4_slice_generation_level_reproduction \
  tests/conformance/test_elaboration_phase5_remediation.py::test_inline_constraint_references_a_real_modeled_input \
  --junitxml=.project/active/elaborator-cutover/evidence/codegen-live.xml -vv -rA
git diff --check

cd /home/reid/1cfe/agentic-mbse
uv run pytest tests/
uv run ruff check src --output-format json
uv run ruff check src tests --output-format json
uv run mypy src --show-error-codes --no-error-summary --no-pretty --hide-error-context
test -n "$SYSIDE_LICENSE_KEY"
env SYSIDE_LICENSE_KEY="$SYSIDE_LICENSE_KEY" uv run pytest -o addopts='' \
  tests/test_validation/test_level4_reconciliation.py::TestLevel4PopulationReconciliation::test_single_file_categories_sum_to_assessed_denominator \
  tests/test_validation/test_item12_checks.py::test_c3_admitted_constraint_is_silent \
  tests/test_sysml/test_constraint_extraction_ordering.py::test_identified_anonymous_usages_keep_exact_ids_when_enumeration_reverses \
  --junitxml=/home/reid/1cfe/sysml-codegen/.project/active/elaborator-cutover/evidence/agentic-live.xml -vv -rA
git diff --check
```

The candidate stores sorted Ruff identities as `{path,line,column,code,message}` JSON and parses
mypy text into the same machine fields. `quality-baseline.json` binds the Item-6 base outputs.
Final-minus-baseline must be empty after removing deleted paths, and any identity in a changed file
fails even if it existed at baseline. `git diff --name-only --diff-filter=ACMR
<base>..<candidate>` defines changed files. Test evidence records command, collected, passed, failed,
skipped, xfailed, deselected, and exit code. Licensed selections must collect at least one test,
pass all, and report zero skip, xfail, or deselection. The exact selections above require codegen
`2 collected/2 passed` and agentic `3 collected/3 passed`; the candidate coordinator parses both
JUnit files and terminal summaries and rejects any count mismatch or license skip. TEAx remains the
separate two-test execution command above. The census scanner, 37 count, exact 15
mappings, no-v5 gate, and accepted candidate ID are additional release gates.

## Next-Stage Handoff

The plan must treat D1–D12, I1–I12, the v6 field set and validation order, the exact Fusion Tea
rename table, the closed census dispositions, and the atomic owner checkpoint as fixed. There are no
open API or architecture choices. The highest-risk first proof is a vertical live → v6 → relocated
route on one runtime fixture with semantic digest equality and a strict tamper case. The second is
the in-place Fusion Tea rename with C25/C2 consumer-set mutations. Do those before bulk test migration
or the sole 37-path recapture.

Planning stays blocked until a focused rereview confirms DR3-F1, DR3-L1, and DR3-L2 against these
durable corrections. Once that review clears them, the next pipeline stage is `$my-plan`, followed
by `$my-implement`; use `$my-audit` for the normal implementation completion gate.

---

Next Step: focused `$my-design-review` of DR3-F1, DR3-L1, and DR3-L2 only
