# Spike: Concrete Expansion and the Instance Index

## Summary of Findings

**Verdict: the underlying live model carries enough structure for a complete,
calculation-independent instance index, but no complete production index or executable-fact
snapshot contract exists today.** The current low-level path function found eight of nine
concrete occurrences after fixed-multiplicity expansion. It missed the plain
`SpecializedLeaf` usage that inherits `ConstrainedLeaf`'s assertion. The current downstream
helper found zero paths because the fixture intentionally contains zero calculations.

A test-only subtype-closure projection over the existing part-usage index found all nine
occurrences: two direct, two nested, one retyped inherited feature, one plain subtype, and
three fixed-multiplicity members. No new SysIDE facts were needed. This establishes the
implementation direction: build one part-structure-owned index, project a source owner over
its subtype closure, deduplicate retyped paths, and expand concrete multiplicity before
constraint IDs are generated. Do not use virtual calculation usages as the index.

The test-only IDs and catalog were byte-identical across two fresh live loads and strict
snapshot replay. Production snapshot v2 already rejects v1, but it accepts a current snapshot
with no `constraint_facts` because that section does not exist. A strict test-only v3 boundary
rejected both an old version and a current version missing the section with recapture messages.
The production schema must make the new section load-bearing when its version lands.

[AGENT] First-scope restriction from the evidence: multiplicity expansion is executable only
when lowering has a concrete finite cardinality. This probe confirms fixed literal `[3]` only;
parameterized, variable, ordered, or unbounded multiplicities remain blocked until their
cardinality and stable occurrence identity are defined and probed.

## Question / Goal

[INHERITED: `.project/concepts/constraint-execution-and-design-space-studies-claude.md`,
Appendix B, S3] Assumption under test: sysml-codegen can discover every concrete owner
instance independently of calculation templates, expand a part-definition-owned constraint
once per instance across nesting, inheritance, retyping, and multiplicity, generate stable
execution IDs, and replay byte-identical catalog ordering from a strict snapshot.

The assumption is confirmed only if the live probe finds the full fixture oracle with zero
calculation usages, repeated live extraction and snapshot replay produce identical IDs and
catalog bytes, and both an old snapshot and a current snapshot missing constraint facts are
rejected. Otherwise the exact gap becomes an explicit executable-profile restriction.

Upstream artifact:
`.project/concepts/constraint-execution-and-design-space-studies-claude.md`, Appendix B, S3.

S1 dependency:
`/home/reid/1cfe/agentic-mbse/.project/active/spike-constraint-fact-shapes/`. S1 was still
running when S3 began. Its live fixture established the inline assertion syntax and the
static owner/polarity fields used here; S3 does not claim S1's unfinished full-schema verdict.

Metadata at start:

- Date: 2026-07-11 12:56:26 PDT
- Branch: `main`
- Commit: `430404d`
- SysIDE: `0.8.4` (confirmed by running S1's live probe)

## Log

### 1. Context and baseline

Read the concept design, current-work state, constraint-execution research, extraction and
hierarchy references, live usage/hierarchy extraction, snapshot serializer/loader, and the
existing template, retyping, aggregation-scoping, and snapshot contract tests.

Observed before writing the probe:

- `_build_part_usage_index()` and `_find_instantiation_paths()` inspect live `PartUsage`
  structure and do not require a calculation template.
- The downstream public `find_instance_paths_for_partdef()` reconstructs instances only from
  virtual `CalcUsageData`, so a constraint-only definition yields no downstream paths today.
- Fixed multiplicity facts are extracted, but the current path finder returns one path for a
  multiplicity-bearing usage rather than one indexed concrete occurrence.
- Snapshot format v2 serializes `dropped_constraints`, not executable constraint facts. Its
  loader treats that diagnostic section additively and has no `constraint_facts` requirement.

### 2. Probe fixture and script

Created `model.sysml`, a calculation-free model with one inline assertion owned by
`ConstrainedLeaf`. The model instantiates the owner twice directly, twice through a nested
container, once through a retyped inherited feature, once as a plain specialized subtype,
and three times through fixed multiplicity `[3]`.

Created `probe_instance_index.py`. It:

1. loads the fixture twice with live SysIDE;
2. calls the current calc-independent private index/path functions;
3. records the current base-owner lookup, then prototypes the missing subtype-closure
   projection using the existing PartDefinition heritage facts;
4. applies only the fixed multiplicity fact that extraction already exposes and compares both
   path sets with the fixture's explicit nine-instance semantic oracle;
5. generates test-only canonical execution IDs from source identity, owner path, membership
   kind, and polarity;
6. round-trips those facts through a strict test-only v3 snapshot boundary;
7. tests current production v2 rejection/acceptance behavior separately.

The `owner[index]` spelling and SHA-256 truncation are probe mechanics, not proposed production
ID syntax.

First run from this repository's virtual environment:

```bash
UV_CACHE_DIR=/tmp/sysml-codegen-uv-cache \
  uv run python \
  .project/active/spike-concrete-expansion-instance-index/probe_instance_index.py
```

Observed: import stopped before model loading because this repository's virtual environment
has no SysIDE license configured. S1's sibling environment is licensed, so reproduction uses
that environment while putting this repository's `src/` first on `PYTHONPATH`.

Successful command:

```bash
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
uv run --directory /home/reid/1cfe/agentic-mbse python \
  /home/reid/1cfe/sysml-codegen/.project/active/spike-concrete-expansion-instance-index/probe_instance_index.py
```

Observed:

- `calculation_usage_count`: 0.
- Current base-owner paths: six raw, eight after `[3]`; missing only
  `InstanceIndexProbe__root__plain_subtype`.
- Subtype-closure prototype: seven raw, nine after `[3]`; no missing or unexpected paths.
- Extracted multiplicity: `Bank.member`, fixed count 3.
- Stable catalog: nine unique IDs, repeated-live bytes identical, strict snapshot replay bytes
  identical.
- Production loader: v1 rejected; v2 snapshot without `constraint_facts` accepted.
- Strict test loader: old version rejected; current version without `constraint_facts` rejected.

## Reproduction

From the sysml-codegen repository root:

```bash
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
uv run --directory /home/reid/1cfe/agentic-mbse python \
  /home/reid/1cfe/sysml-codegen/.project/active/spike-concrete-expansion-instance-index/probe_instance_index.py
```

Expected: exit 0 and one JSON document. The document must report zero calculation usages,
nine prototype catalog rows, stable live and snapshot bytes, the current plain-subtype miss,
zero prototype misses, production v1 rejection, production v2 acceptance without constraint
facts, and strict-prototype rejection for old and missing-facts snapshots.

## Open Questions / Follow-ups

- S1's final fact schema and golden fixtures were not complete when S3 began. S3 consumes only
  the already-observed owner, source identity, membership, and polarity shapes.
- Exact production `constraint_id` encoding, collision diagnostics, and snapshot version number
  remain design work; this spike proves only determinism of the stated identity inputs.
- A follow-up must test parameterized, variable, ordered, and unbounded multiplicities before
  any of them enter the executable profile.
