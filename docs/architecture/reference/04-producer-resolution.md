# 04 -- Producer Resolution: The One Resolution Authority

Every consumer that asks *which real thing produces this consumed value?* answers
it in exactly one place: `resolve_producer()` in
`resolution/producer_resolution.py`. A calculation binding, a constraint actual,
and an aggregation term all build a `ProducerRequest` and read a
`ProducerResolution`. The ordered key-form table, the self-reference guard, and
the terminal fork live in that module and nowhere else (lifecycle Item 2).

This replaced three separate resolver ladders — the calculation ladder, the
constraint ladder, and the aggregation strategy chain — that each invented
their own lookup order, guard placement, and terminal behavior and had drifted
apart. The old standalone aggregation resolver module was deleted;
[24-dual-resolution-architecture](24-dual-resolution-architecture.md) records
what it was. See [24-dual-resolution-architecture](24-dual-resolution-architecture.md)
for the before/after and the one structural distinction that remains (calc
bindings resolve *during* the backtracker's DFS; other consumers resolve after).

## The mental model: tier versus key form

Two ideas, kept separate (`producer_resolution.py:9-28`):

- A **tier** is a claim about what *class of thing* may produce a value. Contract
  invariant 19 names two: a real producer channel (an upstream module's output),
  then a real design attribute under exact qualified identity. Tier 1 (`CHANNEL`)
  is exhausted before tier 2 (`DESIGN_ATTRIBUTE`).
- A **key form** is one *way of asking* "is it here?" — one way to build a lookup
  key from the reference and the consumer's scope. There are many key forms
  (the table has 21), and nearly all are exact keyed lookups.

The old ladders did not drift because they tried many key forms. They drifted
because each invented its own list. So the forms are declared as **data**, in one
order, and a consumer cannot add, reorder, or skip one.

## The single entry point

```python
def resolve_producer(
    request: ProducerRequest, context: ProducerContext
) -> ProducerResolution
```

`resolve_producer` (`producer_resolution.py:616`) runs the declared table in
order — tier 1 before tier 2 — applying the self-reference guard at every tier-1
hit and the lenient-only admissibility rule at every row. Then it runs the tier-1
terminal search (the scope climb). Then, and only then, it reads the terminal
policy. It is the only positive-resolution path in the tree (design invariant I1).

Every resolution is also recorded to the active capture sink, which the
[producer-completeness check](#the-producer-completeness-check) reads. Capture is
centralized here so all consumer call sites are covered by construction
(`producer_resolution.py:625-636`).

### ProducerRequest — the consumer's question, as data

Frozen dataclass (`producer_resolution.py:99`). The load-bearing fields:

| Field | Meaning |
|---|---|
| `consumer_eqn` | Producing-module [EQN](15-naming-conventions.md) of the asker. Sole input to the self-reference guard and to the entry-point QN rule. |
| `reference` | The reference the consumer holds, never pre-split. |
| `param_name` | The consumer's declared formal name, where it has one. Drives the entry-point QN. |
| `consumer_scope` | Dotted scope the reference is read in. |
| `policy` | `STRICT` or `LENIENT`. Read once, after the table; also gates which key forms are admissible. |
| `diagnostic_context` | Consumer-supplied text for the strict error / lenient warning. |
| `instance_path`, `owner_def_qn`, `target_qn`, `parent_scope`, `written_reference`, `occurrence_owner_path` | Dedicated inputs for specific rows (occurrence-materialized QN, direct channel, target QN, def-scoped QN). Each is read at a small, named set of rows so one consumer can reach a row without perturbing what other rows see. |

### ProducerResolution — what the table produced

Frozen dataclass (`producer_resolution.py:132`). `outcome` is one of
`MODULE_OUTPUT`, `DESIGN_ATTRIBUTE`, or `ENTRY_POINT`; `identity` is the channel,
design-attribute QN, or minted entry-point QN. `key_form` records which form
produced it (precedence is observable); `attempted` lists the forms tried in
order (strict-error context); `ambiguous_candidates` carries the identities that
tied within a form.

### ProducerContext — everything the table may read

Frozen dataclass (`producer_resolution.py:181`), built once per run: the
[OutputRegistry](10-output-registry.md), the by-QN design-attribute map, the
design-attribute list (for the name-based forms), redefinitions, the
`usage_type_map`, and the calc-def QN set used by the calc-def-owned filter.

## The KEY_FORMS ladder

`KEY_FORMS` (`producer_resolution.py:527`) is one ordered, tier-partitioned,
policy-annotated tuple. Each entry declares its number, name, tier, lookup
function, and whether it is `lenient_only`. The table as it stands at merged main:

**Tier 1 — real producer channel** (`CHANNEL`)

| # | Key form | Lenient-only? |
|---|---|:-:|
| 1 | `scoped_prefixed` — consumer-scope-prefixed scoped key | |
| 2 | `scoped_deindexed` — de-indexed occurrence scope | |
| 3 | `scoped_bare` — the bare reference as a scoped key | |
| 4 | `alias_prefixed` — consumer-scope-prefixed alias key | |
| 5 | `alias_deindexed` — de-indexed alias key | |
| 6 | `scoped_alias_prefixed` — structured `(scope, leaf)` alias, scope-prefixed | |
| 7 | `scoped_alias_deindexed` — structured alias, de-indexed scope | |
| 8 | `structured_alias_unscoped` — structured alias, no scope | |
| 9 | `structured_alias_deindexed` — structured alias, de-indexed prefix | |
| 10 | `alias_bare` — bare reference against the alias registry | |
| 11 | `sysml_qn` — sanitized SysML QN lookup | |
| 12 | `direct_channel` — construct a CalcUsage-format channel, membership-checked | |
| 13 | `chain_redefinition_follow` — follow `:>>` CHAIN redefinitions to a channel | L |
| 14 | `leaf_parent_scoped` — leaf recombined with the consumer's parent part | L |
| 15 | `leaf_consumer_scoped` — leaf recombined with the consumer's full scope | L |

**Tier-1 terminal search — the scope climb** (`_scope_climb`,
`producer_resolution.py:580`). Not a table row. After the tier-1 rows miss, it
retries the scoped key under each ancestor prefix of the consumer scope, collects
every distinct non-self-referential channel, and returns one **only when they
agree** — that collect-then-require-unique behavior is why it is not modeled as an
ordered row. Gated to 3+-segment references.

**Tier 2 — real design attribute under exact qualified identity**
(`DESIGN_ATTRIBUTE`)

| # | Key form | Lenient-only? |
|---|---|:-:|
| 16 | `occurrence_materialized_qn` — the design attribute materialized under its owning occurrence | |
| 17 | `target_qn` — the resolved target QN, exact | |
| 18 | `owner_def_qn` — the reference under the owning-definition QN | |
| 19 | `dotted_pair` — dotted reference matched as `(first segment, leaf)`, unique-or-refuse | L |
| 20 | `leaf_unique` — leaf name unique across files, calc-def-owned filtered out | L |
| 21 | `bare_name_unique` — bare reference matched by attribute name, unique-or-refuse | L |

### Name-based forms are lenient-only, and never guess

The rows marked `L` identify a candidate by *name* rather than by exact key.
Every one of them **refuses rather than guesses**: it returns a result only when
exactly one candidate survives, and records the tied candidates otherwise
(`_unique_or_tie`, `producer_resolution.py:465`). This is design invariant I3 —
name-based *identification* is allowed; guessing among what it finds is not.

Because they are `lenient_only`, they are **unreachable from the strict constraint
consumer** (`_admissible`, `producer_resolution.py:606`), which is exactly where
they are unreachable today: all of that consumer's lookups are exact.

### The self-reference guard

One predicate — `channel.rsplit("__", 1)[0] == consumer_eqn`
(`_is_self_reference`, `producer_resolution.py:568`) — applied at **every** tier-1
hit for **every** consumer (design invariant I6). A consumer's input may not
resolve to a channel its own module produces; that is a cycle. A rejection **skips
the candidate and continues the table** rather than abandoning the remaining keys.
Before Item 2 this guard sat at three different granularities and was missing from
two paths entirely.

## The terminal fork: strict versus lenient

The whole strict/lenient difference is one branch, in one place —
`_terminal_miss` (`producer_resolution.py:688`), reached only after the table and
the climb have missed. It is selected by `request.policy` (`TerminalPolicy`,
`producer_resolution.py:84`):

- **STRICT** raises `CodeGenerationError`, naming the reference, the key forms
  attempted, and any tied candidates ("no fallback, no entry-point synthesis —
  INV-2"). The strict miss raises *before* returning, so it never reaches the
  capture sink. This is the constraint consumer: a constraint actual never invents
  a value or takes a fallback.
- **LENIENT** mints one entry point. Its QN comes from `entry_point_qualified_name`
  (`producer_resolution.py:553`): `f"{consumer_eqn}__{key}"`, where `key` is the
  declared formal `param_name` when the consumer has one, and the flattened
  reference (`reference.replace(".", "_")`) when it does not. This one rule
  reproduces all three pre-unification entry-point formulas byte-for-byte. A lenient
  miss also emits one warning at the call site (design invariant I7).

Answering the tired-engineer question directly: **what resolves an input** is the
first admissible key form that hits, tier 1 before tier 2; **in what order**, the
declared `KEY_FORMS` sequence then the scope climb; **on a miss**, STRICT raises
and LENIENT mints one entry point.

## The three consumer paths

Each consumer is a request builder and a result reader. None owns any ordering,
key construction, or terminal behavior.

### Constraint actual — STRICT

`resolve_actual` (`analysis/constraint_lowering.py:149`, calling
`resolve_producer` at `:174`) lowers one constraint actual. Its policy is
`STRICT`, the only thing distinguishing it from the other two consumers: no
name-based form is admissible, so the forms it can reach are exactly the
exact-identity ones. A `MODULE_OUTPUT` outcome becomes a channel-bound input; a
`DESIGN_ATTRIBUTE` outcome becomes a design-attribute input.

### Calculation binding — LENIENT

`_resolve_binding_via_registry`
(`analysis/dependency_backtracker.py:571`, calling `resolve_producer` at `:596`)
resolves one calculation binding during the backtracker's DFS. Its policy is
`LENIENT`, so a terminal miss yields one typed entry point rather than raising.
Its `reference` is the referent's *resolved* qualified name, so it supplies the
reference *as written* through the dedicated `written_reference` field (which row
16 reads); this is what lets the shared attribute reach the same
occurrence-materialized key the constraint consumer reaches (DD-R27). Only this
consumer's lenient miss is recorded to `fallback_entry_points` for V11 coverage
(design invariant I10) — aggregation misses are deliberately not.

### Aggregation term — LENIENT

Aggregation resolution runs through the shared table at three call sites in
`resolution/graph_builder.py`, all `LENIENT`:

- `_build_agg_input_source` (`:1369`, calling `resolve_producer` at `:1403`) —
  the SumTerm/SingletonTerm choke point. A `MODULE_OUTPUT` wires directly; a
  terminal miss looks up a `LITERAL :>>` default, mints a `DESIGN_ATTRIBUTE` entry
  point with that default, and reports `manual_required` when there is no default.
- The LocalTerm EXPOSE-alias reroute (`:1640`) — takes the resolved channel
  **only** on a `MODULE_OUTPUT` (the D5 guard); anything else falls through to
  LocalTerm's own mint, which keeps the `{module_eqn}__{attribute_name}` key.
- The LocalTerm plain-attribute path (`:1663`) — asks the table before minting, so
  a literal-valued attribute on the aggregating part def resolves as a real design
  attribute instead of a defaultless entry point.

FORMULA modules are the one resolution mechanism that does **not** call
`resolve_producer`: they use a pre-computed
[attribute resolution map](16-computed-attributes.md) built at classification
time, where channels are already known and no lookup is needed.

## The producer-completeness check

`check_producer_completeness` (`resolution/producer_completeness.py:98`) is
separate from and additive to V11 coverage. V11 proves no wired input references a
valueless key; producer completeness proves every model-derived consumed value
resolved to **one intended producer**. It reads the resolver's recorded outcomes
from the capture sink — it does **not** re-resolve — and flags two kinds
(`CompletenessViolationKind`, `producer_completeness.py:75`):

- **Ambiguous producer** — a resolution that saw a same-leaf tie
  (`ambiguous_candidates` non-empty). The resolver refused to guess and fell
  through to an entry point carrying the tied QNs.
- **Leaf-name guess** — a *qualified* reference (`part.attr`) that resolved
  through a name-based lenient row and dropped its scope qualifier. This spans
  both the tier-2 rows (`dotted_pair` / `leaf_unique` / `bare_name_unique`) and
  the tier-1 name-based channel rows (`leaf_parent_scoped` / `leaf_consumer_scoped`)
  — the same defect whether it lands on a design attribute or a module output
  (`NAME_BASED_KEY_FORMS`, `producer_completeness.py:64`). A *bare* reference
  matched by name is not flagged: with no qualifier to drop and a unique candidate,
  that is the intended producer resolved by its only handle.

What it does not flag: a clean `ENTRY_POINT` with no ties and no name-based form (a
legitimate external declared input, exempt by owner decision D-1), and any
`MODULE_OUTPUT` or exact-QN `DESIGN_ATTRIBUTE` resolved through an exact or
structural row (these consult the reference's own owner — the conformant path).

## Related Documents

- **Upstream**: [03-resolution-overview](03-resolution-overview.md),
  [01-extraction](01-extraction.md)
- **Downstream**: [05-module-factory](05-module-factory.md),
  [06-entry-point-classifier](06-entry-point-classifier.md)
- **Architecture**: [24-dual-resolution-architecture](24-dual-resolution-architecture.md)
  — the pre-unification story and the DFS-timing distinction that remains
- **Registry**: [10-output-registry](10-output-registry.md),
  [15-naming-conventions](15-naming-conventions.md) — typed identifiers and channel formats
- **Data models**: [09-data-models](09-data-models.md) — InputSource, PipelineModule
