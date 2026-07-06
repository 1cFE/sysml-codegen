# Conformance tests — how to anchor an expectation

A conformance test proves the generated package is the truth. It can only do that if
its expected value comes from somewhere **other** than the code under test. This note
records the one anti-pattern to avoid and how to anchor an expectation instead.

## The anti-pattern: a test that cannot fail

```python
expected = production_fn(x)      # the same call the code under test makes
actual = thing_under_test(x)
assert actual == expected
```

Both sides come from one code path, so the assertion is `f(x) == f(x)` — true for any
`x`, including a buggy one. The test is green forever and pins nothing. This is banned
(epic R1). It hides in several shapes:

- Recomputing the production helper: `expected = get_channel_name(module_eqn, attr)`.
- Re-invoking the gating call: a branch entered because `default_value is None`, then
  asserting `_get_library_default(...) is None`.
- Self-shaped expectations: `expected = f"tuple[{', '.join(['float']*n)}]"` — the `n`
  rides the same data as the actual.
- Comparing two `len(...)` over one 1:1 loop: `len(files) == len(groups)`.

## The fix: transcribe a literal from a known fixture element

Read a concrete value out of a committed source and hardcode it, with a provenance
comment saying where it came from:

```python
# provenance: tests/fixtures/catf_mfe_model/extraction_snapshot.json:4527
#   (literal_value 1546.72 bound to auxiliary_load.gross_electric)
assert ep.default_value == 1546.72
```

Rules that make a literal trustworthy:

- **Committed source only.** Draw from the snapshots
  (`tests/fixtures/{model}/extraction_snapshot.json`), the `computation_graph.json`
  baselines, or the `*.sysml` design/library sources. License-free — no live extraction.
- **Every literal carries a provenance comment** next to it (snapshot path + line,
  fixture `file:line`, or "hand-computed from <inputs>"). This is the review-time defense
  against a value pasted from production output.
- **Select fixture elements by identity, not list index.** For aggregations, pick by
  `(instance_path, attribute_name)` — index is a DFS-order artifact and a reorder must
  not move the pin.
- **A deliberate PQN doubling is not a typo.** An aggregation/FORMULA output channel
  repeats its trailing segment (e.g. `…__capital_cost__capital_cost`) — ADR-003,
  `get_channel_name` composes `usage_qn + "__" + output_name` and the module EQN already
  ends in the attribute name. Keep it doubled; comment it.

## The pass-or-skip trap

A test that can only pass or skip is not coverage — a green suite hides that it never
ran an assertion. Set the found-flag inside the loop, then end on an **unconditional**
assert, never `pytest.skip`:

```python
found = False
for ...:
    if <the element we require>:
        assert <the real property>
        found = True
assert found, "the required fixture element was not present"
```

## Existing conventions to reuse

- **`req(id)` marker** maps a test to a requirement (`tests/conformance/conftest.py:66`).
- **Snapshot fixtures** load committed extraction snapshots
  (`tests/conformance/conftest.py:70-91`: `extraction_snapshots`, `solar_battery_snapshot`,
  `catf_mfe_snapshot`).
- **Exemplar literal tables** to copy the style from:
  `tests/conformance/test_naming_conventions.py:93-149` (`REAL_EQNS`, `PQN_EXAMPLES`) and
  the literal type-map tests in `tests/conformance/test_gen_schemas.py:355-381`.
