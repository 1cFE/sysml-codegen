# SysIDE identity and redefinition probe record

- **Date:** 2026-08-08 10:32:43 PDT
- **Branch:** `source-identity-epic`
- **Commit:** `6bed968`
- **SysIDE version:** `0.8.4` (`uv.lock:749-760`)
- **Purpose:** Persist the load-bearing probe facts used by the exact identity bridge design.

## Evidence provenance

- **[AGENT]** The reopened design session checked SysIDE's installed type surface and ran
  read-only cross-load probes over the elaborator fixtures.
- **[INHERITED: `.project/active/elaborator-design/design-review.md`]** The independent design
  reviewer reran the identity probe with relocation and model-edit variants and ran the implied
  redefinition probe against `spec_chain_twolevel`.
- The review session's throwaway probe scripts were not retained. This record preserves the
  observed inputs and outcomes. The implementation plan must replace this session evidence with
  kept automated tests before identity-dependent breadth work starts.

## Probe 1 — named-element identity across loads

The probes loaded the same licensed fixture models in independent SysIDE documents and compared
`element_id` values for named executable declarations and the IDs reached through resolved
referents.

Observed:

- 33 of 33 sampled named elements retained the same UUID across independent loads.
- The same IDs survived a relocated fixture directory, source-offset shifts, and unrelated model
  edits in the reviewer's variants. Earlier probes also covered reversed input-file order and
  relative versus absolute model paths.
- A resolved referent's `element_id` equaled the ID read directly from the referred declaration.
- Python object hashes changed between loads. They are valid only inside one live document.
- Stable generated IDs in the sample were UUIDv5 values derived by SysIDE from qualified names.

The installed SysIDE stub states a narrower contract than “every element is reload-stable.” It says
`element_id` is globally unique and immutable during an element's lifetime, but currently stable
across rebuilds only for elements with qualified names and their owning memberships. It also says
the property may be deprecated because SysIDE regards it as serialization support
(`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:5875-5905`).

## Probe 2 — null-qualified-name identity boundary

Observed null-qualified-name elements used generated UUIDv4 values that changed across independent
loads. The sample included:

- named elements whose qualified name is null because of a same-name namespace collision;
- anonymous usages;
- expression objects; and
- relationship objects, including the `Redefinition` relationship object itself.

Consequences:

- Codegen may consume a declaration UUID that SysIDE produced from a qualified name without ever
  using the qualified-name string as a lookup key. The parser resolves the object; codegen consumes
  its UUID. Cross-load stability nevertheless depends on SysIDE's current qualified-name-derived ID
  implementation, so the supported SysIDE version and stability tests are part of the boundary.
- An executable declaration or containment usage without a reload-stable ID cannot enter a
  projectable, serializable graph. A stable owning-membership ID is a possible exact coordinate, but
  it must be proven before use. Until then, the form fails closed.
- Expression and relationship objects do not need graph identity. References and redefinition
  families key from their resolved endpoint declaration IDs. In particular, codegen must never use
  a `Redefinition` relationship object's random ID as the feature-slot key.

## Probe 3 — implicit parameter redefinitions are real edges

The reviewer loaded `spec_chain_twolevel` and inspected the calculation usage parameter authored as
`in drive_power = ...`.

Observed:

- The usage-side parameter owned one materialized `Redefinition` relationship.
- `redefined_feature` pointed to `MeierCost::drive_power`.
- The relationship had `is_implied=True`. The definition-side parameter was the slot root and owned
  no redefinition edge.
- Authored `:>>` used the same endpoint shape with `is_implied=False`.
- `is_implied_included` was true for both forms and therefore does not distinguish them.
- The semantic endpoints are `redefined_feature` and `redefining_feature`; the relationship does not
  expose generic `source`/`target` endpoints
  (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:14795-14833`).

Consequences:

- A feature-slot family follows every SysIDE-materialized `Redefinition` edge, whether authored or
  implied. Filtering out implied edges would split ordinary calculation usage bindings from their
  formal parameter slots.
- The edge's authored/implied status is provenance, not an inclusion filter.
- Slot identity comes from endpoint declaration IDs and the unique root of their redefinition
  family.

## Required kept kill probes

Before further consumer-shape breadth work, automated licensed tests must pin:

1. Named declaration ID stability and referent-ID equality across independent loads, relocation,
   file-order changes, and harmless model edits.
2. The exact fail-closed result for an executable or containment declaration whose identity is not
   reload-stable, including same-name/null-QN and anonymous cases.
3. Ordinary implied parameter redefinitions and authored `:>>` redefinitions joining the same slot
   through endpoint IDs.
4. A reversed relationship/iteration order producing the same slot root and graph edge.
5. A guard that relationship-object IDs, names, qualified names, and rendered paths cannot become
   slot, occurrence, or edge lookup keys.

Failure of any probe is an identity-foundation stop condition. It is not deferred to end-stage
acceptance.

## Kept kill-probe execution — 2026-08-08

**[AGENT]** Phase 1 replaced the session-only evidence with these kept licensed tests:

- `tests/conformance/test_elaboration_identity_foundation.py` — four tests covering independent
  loads, reversed files, relocated roots, harmless source/model edits, referent equality, UUID
  versions, authored/implied endpoint stability, relationship-ID instability, and the null-QN
  executable/containment boundary.
- `../agentic-mbse/tests/test_sysml/test_syside_identity_contract.py` — three tests covering the
  raw parser `element_id`, resolved referent, feature-chain target, typing target, and authored plus
  implied `Redefinition` endpoint surfaces.
- `tests/fixtures/elab_identity_collision_probe/model.sysml` — the required same-name/null-QN and
  anonymous-containment negative fixture. The sibling and shadowing fixtures did not expose a
  null-QN executable declaration, so this fixture was necessary.

Commands and observed outcomes:

- `uv run pytest tests/conformance/test_elaboration_identity_foundation.py -q` — **4 passed**, all
  collected, zero license-skip lines.
- From `../agentic-mbse`,
  `uv run pytest tests/test_sysml/test_syside_identity_contract.py -q` — **3 passed**, all
  collected, zero license-skip lines.
- Ruff on both new test files — passed.

The tests perform relocation and reversed-order loads internally. Named declarations, resolved
referents, typing targets, and redefinition endpoints remain UUIDv5-stable. Null-QN executable and
containment declarations and `Redefinition` relationship objects remain UUIDv4 and change between
loads. No relationship-object ID is accepted as declaration or slot identity.
