# Captured red: the Item 4 characterizations with their `xfail` markers stripped

**Why this file exists.** Both trees must be green at every commit (the companion is an
editable install, so a companion commit is live for codegen the instant it lands), and the
epic's posture is red-first. D8 reconciles the two: the characterizations land as
`@pytest.mark.xfail(strict=True)`, so the tree is green while the tests are genuinely red.
That makes "they were red" a claim rather than a fact — unless the marker-removed run is
captured as output. This is that output (design review A3).

**Run.**

```
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
  tests/conformance/test_predicate_unit_annotation.py \
  tests/conformance/test_constraint_binding_unit_annotation.py \
  tests/conformance/test_blocked_chain_diagnostic.py \
  tests/unit/test_render_block_reasons.py -q
```

**State.** codegen `item7-rebuild` @ `3ca94af` (fixtures and test files added, working tree);
companion `item7-rebuild` @ `bc69f04`, untouched. Date: 2026-08-13.

**Result: 20 failed, 6 passed.** The same 26 tests with the markers in place read
`6 passed, 20 xfailed` — the counts match exactly, so every marker is carrying a real
failure and none is masking a pass.

The 6 that pass before the fix are the guards that must also pass after it:

| Test | What it guards |
|---|---|
| `test_an_incompatible_annotation_still_blocks_on_a_dimension_reason` | invariant 2 on the companion path (design review A1: not a discriminator) |
| `test_a_genuine_expression_source_is_still_refused` | D2's bound — `a + b` stays refused |
| `test_two_elaborations_of_one_model_produce_byte_identical_detail` | determinism, which the fix is what could break |
| `test_the_detail_is_a_single_line` | invariant 8 |
| `test_one_blocked_constraint_node_still_yields_one_diagnostic` | invariant 4 — the row count does not move |
| `test_an_asserted_blocked_chain_still_halts` | the Item 2 contract |

## Defect A — the reproduction, in one line

```
ElaborationDiagnosticError: SI_OCCURRENCE_MISSING:
predicate_unit_annotation__the_host__gap_guard:
leaf declaration 146016c8-c0f8-5b9b-882d-33c75906e6ee has no feature slot
```

## Defect B — the tautology, in one line

```
constraint profile blocked execution: block_feature_chain: feature_chain:
block_feature_chain; block_feature_chain: feature_chain: block_feature_chain;
block_feature_chain: feature_chain: block_feature_chain
```

Three chain occurrences over two distinct references, rendered as three identical copies
of a string that names neither.

## The fourth lane — both annotated bindings refused

```
AssertionError: assert not ['constraint_binding_unit_annotation__Host__band.ref_value',
                            'constraint_binding_unit_annotation__Host__band.tol']
```

## Full output, verbatim

```
============================= test session starts ==============================
platform linux -- Python 3.12.11, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/reid/1cfe/sysml-codegen-item7-rebuild
configfile: pyproject.toml
plugins: cov-7.1.0
collected 26 items

tests/conformance/test_predicate_unit_annotation.py FFFF.F               [ 23%]
tests/conformance/test_constraint_binding_unit_annotation.py FFF.        [ 38%]
tests/conformance/test_blocked_chain_diagnostic.py FFFF....              [ 69%]
tests/unit/test_render_block_reasons.py FFFFFFFF                         [100%]

=================================== FAILURES ===================================
_______ test_an_asserted_predicate_carrying_a_unit_annotation_elaborates _______
tests/conformance/test_predicate_unit_annotation.py:64: in test_an_asserted_predicate_carrying_a_unit_annotation_elaborates
    graph = elaborate_model_paths([ANNOTATED])
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/orchestration/elaborated_pipeline.py:65: in elaborate_model_paths
    graph = elaborate(
src/sysml_codegen/elaboration/elaborate.py:269: in elaborate
    return _ExactElaborator(model, calc_defs, strict=strict).run()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/elaboration/elaborate.py:521: in run
    raise ElaborationDiagnosticError(self._graph.diagnostics)
E   sysml_codegen.elaboration.elaborate.ElaborationDiagnosticError: SI_OCCURRENCE_MISSING: predicate_unit_annotation__the_host__gap_guard: leaf declaration 146016c8-c0f8-5b9b-882d-33c75906e6ee has no feature slot
__________________ test_the_cured_predicate_is_a_working_gate __________________
tests/conformance/test_predicate_unit_annotation.py:70: in test_the_cured_predicate_is_a_working_gate
    row = _gap_guard_row(ANNOTATED)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
tests/conformance/test_predicate_unit_annotation.py:43: in _gap_guard_row
    catalog = build_elaborated_pipeline([fixture]).constraint_catalog
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/orchestration/elaborated_pipeline.py:42: in build_elaborated_pipeline
    return project(elaborate_model_paths(model_paths))
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/orchestration/elaborated_pipeline.py:65: in elaborate_model_paths
    graph = elaborate(
src/sysml_codegen/elaboration/elaborate.py:269: in elaborate
    return _ExactElaborator(model, calc_defs, strict=strict).run()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/elaboration/elaborate.py:521: in run
    raise ElaborationDiagnosticError(self._graph.diagnostics)
E   sysml_codegen.elaboration.elaborate.ElaborationDiagnosticError: SI_OCCURRENCE_MISSING: predicate_unit_annotation__the_host__gap_guard: leaf declaration 146016c8-c0f8-5b9b-882d-33c75906e6ee has no feature slot
_________________ test_the_unit_is_not_resolved_as_a_reference _________________
tests/conformance/test_predicate_unit_annotation.py:87: in test_the_unit_is_not_resolved_as_a_reference
    graph = build_elaborated_pipeline([ANNOTATED])
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/orchestration/elaborated_pipeline.py:42: in build_elaborated_pipeline
    return project(elaborate_model_paths(model_paths))
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/orchestration/elaborated_pipeline.py:65: in elaborate_model_paths
    graph = elaborate(
src/sysml_codegen/elaboration/elaborate.py:269: in elaborate
    return _ExactElaborator(model, calc_defs, strict=strict).run()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/elaboration/elaborate.py:521: in run
    raise ElaborationDiagnosticError(self._graph.diagnostics)
E   sysml_codegen.elaboration.elaborate.ElaborationDiagnosticError: SI_OCCURRENCE_MISSING: predicate_unit_annotation__the_host__gap_guard: leaf declaration 146016c8-c0f8-5b9b-882d-33c75906e6ee has no feature slot
______ test_the_annotated_and_bare_twins_produce_identical_module_inputs _______
tests/conformance/test_predicate_unit_annotation.py:96: in test_the_annotated_and_bare_twins_produce_identical_module_inputs
    assert _module_inputs(ANNOTATED) == _module_inputs(BARE)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
tests/conformance/test_predicate_unit_annotation.py:54: in _module_inputs
    graph = build_elaborated_pipeline([fixture])
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/orchestration/elaborated_pipeline.py:42: in build_elaborated_pipeline
    return project(elaborate_model_paths(model_paths))
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/orchestration/elaborated_pipeline.py:65: in elaborate_model_paths
    graph = elaborate(
src/sysml_codegen/elaboration/elaborate.py:269: in elaborate
    return _ExactElaborator(model, calc_defs, strict=strict).run()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/sysml_codegen/elaboration/elaborate.py:521: in run
    raise ElaborationDiagnosticError(self._graph.diagnostics)
E   sysml_codegen.elaboration.elaborate.ElaborationDiagnosticError: SI_OCCURRENCE_MISSING: predicate_unit_annotation__the_host__gap_guard: leaf declaration 146016c8-c0f8-5b9b-882d-33c75906e6ee has no feature slot
___________ test_a_malformed_annotation_in_a_predicate_hard_refuses ____________
tests/conformance/test_predicate_unit_annotation.py:132: in test_a_malformed_annotation_in_a_predicate_hard_refuses
    with pytest.raises(ElaborationInvariantError) as refusal:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE ElaborationInvariantError
____________ test_an_annotated_literal_binding_is_read_as_its_value ____________
tests/conformance/test_constraint_binding_unit_annotation.py:68: in test_an_annotated_literal_binding_is_read_as_its_value
    assert _bindings(graph, "__band")["tol"] == LiteralInput(0.05)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'tol'
__________ test_an_annotated_reference_binding_is_read_as_a_reference __________
tests/conformance/test_constraint_binding_unit_annotation.py:73: in test_an_annotated_reference_binding_is_read_as_a_reference
    assert isinstance(_bindings(graph, "__band")["ref_value"], NodeRef)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'ref_value'
______ test_neither_annotated_binding_is_refused_as_an_expression_source _______
tests/conformance/test_constraint_binding_unit_annotation.py:79: in test_neither_annotated_binding_is_refused_as_an_expression_source
    assert not [name for name in _refused_formals(graph) if "__band." in name]
E   AssertionError: assert not ['constraint_binding_unit_annotation__Host__band.ref_value', 'constraint_binding_unit_annotation__Host__band.tol']
_____________ test_the_detail_names_each_blocked_chain_as_authored _____________
tests/conformance/test_blocked_chain_diagnostic.py:60: in test_the_detail_names_each_blocked_chain_as_authored
    assert "bioshield.outer_radius" in detail
E   AssertionError: assert 'bioshield.outer_radius' in 'constraint profile blocked execution: block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain'
_________________ test_the_detail_states_the_bindings_rewrite __________________
tests/conformance/test_blocked_chain_diagnostic.py:67: in test_the_detail_states_the_bindings_rewrite
    assert "in outer_radius = bioshield.outer_radius;" in detail
E   AssertionError: assert 'in outer_radius = bioshield.outer_radius;' in 'constraint profile blocked execution: block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain'
____________ test_the_detail_names_the_source_location_by_basename _____________
tests/conformance/test_blocked_chain_diagnostic.py:74: in test_the_detail_names_the_source_location_by_basename
    assert re.search(r"\[model\.sysml:\d+\]", detail)
E   AssertionError: assert None
E    +  where None = <function search at 0x7b44172c7880>('\\[model\\.sysml:\\d+\\]', 'constraint profile blocked execution: block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain')
E    +    where <function search at 0x7b44172c7880> = re.search
________ test_three_chain_occurrences_collapse_to_two_distinct_entries _________
tests/conformance/test_blocked_chain_diagnostic.py:80: in test_three_chain_occurrences_collapse_to_two_distinct_entries
    assert _blocked_detail().count("block_feature_chain") == 2
E   AssertionError: assert 6 == 2
E    +  where 6 = <built-in method count of str object at 0x7b43f2bba830>('block_feature_chain')
E    +    where <built-in method count of str object at 0x7b43f2bba830> = 'constraint profile blocked execution: block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain'.count
E    +      where 'constraint profile blocked execution: block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain; block_feature_chain: feature_chain: block_feature_chain' = _blocked_detail()
_____________ test_a_present_location_renders_as_basename_and_line _____________
tests/unit/test_render_block_reasons.py:48: in test_a_present_location_renders_as_basename_and_line
    assert _render_block_reasons([_diagnostic()]) == (
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_render_block_reasons.py:26: in _render_block_reasons
    from sysml_codegen.elaboration.elaborate import _render_block_reasons as renderer
E   ImportError: cannot import name '_render_block_reasons' from 'sysml_codegen.elaboration.elaborate' (/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/elaboration/elaborate.py)
______ test_an_absent_location_renders_no_suffix_at_all[no-location-fact] ______
tests/unit/test_render_block_reasons.py:64: in test_an_absent_location_renders_no_suffix_at_all
    rendered = _render_block_reasons([_diagnostic(location=location)])
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_render_block_reasons.py:26: in _render_block_reasons
    from sysml_codegen.elaboration.elaborate import _render_block_reasons as renderer
E   ImportError: cannot import name '_render_block_reasons' from 'sysml_codegen.elaboration.elaborate' (/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/elaboration/elaborate.py)
_________ test_an_absent_location_renders_no_suffix_at_all[empty-file] _________
tests/unit/test_render_block_reasons.py:64: in test_an_absent_location_renders_no_suffix_at_all
    rendered = _render_block_reasons([_diagnostic(location=location)])
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_render_block_reasons.py:26: in _render_block_reasons
    from sysml_codegen.elaboration.elaborate import _render_block_reasons as renderer
E   ImportError: cannot import name '_render_block_reasons' from 'sysml_codegen.elaboration.elaborate' (/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/elaboration/elaborate.py)
__________ test_an_absent_location_renders_no_suffix_at_all[no-line] ___________
tests/unit/test_render_block_reasons.py:64: in test_an_absent_location_renders_no_suffix_at_all
    rendered = _render_block_reasons([_diagnostic(location=location)])
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_render_block_reasons.py:26: in _render_block_reasons
    from sysml_codegen.elaboration.elaborate import _render_block_reasons as renderer
E   ImportError: cannot import name '_render_block_reasons' from 'sysml_codegen.elaboration.elaborate' (/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/elaboration/elaborate.py)
_____________ test_a_none_line_or_column_never_raises_at_sort_time _____________
tests/unit/test_render_block_reasons.py:75: in test_a_none_line_or_column_never_raises_at_sort_time
    assert _render_block_reasons(diagnostics).count("; ") == 2
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_render_block_reasons.py:26: in _render_block_reasons
    from sysml_codegen.elaboration.elaborate import _render_block_reasons as renderer
E   ImportError: cannot import name '_render_block_reasons' from 'sysml_codegen.elaboration.elaborate' (/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/elaboration/elaborate.py)
_______________ test_identical_diagnostics_collapse_to_one_entry _______________
tests/unit/test_render_block_reasons.py:80: in test_identical_diagnostics_collapse_to_one_entry
    assert _render_block_reasons([_diagnostic()] * 13) == _render_block_reasons([_diagnostic()])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_render_block_reasons.py:26: in _render_block_reasons
    from sysml_codegen.elaboration.elaborate import _render_block_reasons as renderer
E   ImportError: cannot import name '_render_block_reasons' from 'sysml_codegen.elaboration.elaborate' (/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/elaboration/elaborate.py)
__________ test_two_entries_differing_only_in_construct_order_stably ___________
tests/unit/test_render_block_reasons.py:87: in test_two_entries_differing_only_in_construct_order_stably
    assert _render_block_reasons([first, second]) == _render_block_reasons([second, first])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_render_block_reasons.py:26: in _render_block_reasons
    from sysml_codegen.elaboration.elaborate import _render_block_reasons as renderer
E   ImportError: cannot import name '_render_block_reasons' from 'sysml_codegen.elaboration.elaborate' (/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/elaboration/elaborate.py)
_____________________ test_the_rendered_detail_is_one_line _____________________
tests/unit/test_render_block_reasons.py:92: in test_the_rendered_detail_is_one_line
    rendered = _render_block_reasons(
tests/unit/test_render_block_reasons.py:26: in _render_block_reasons
    from sysml_codegen.elaboration.elaborate import _render_block_reasons as renderer
E   ImportError: cannot import name '_render_block_reasons' from 'sysml_codegen.elaboration.elaborate' (/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/elaboration/elaborate.py)
=========================== short test summary info ============================
FAILED tests/conformance/test_predicate_unit_annotation.py::test_an_asserted_predicate_carrying_a_unit_annotation_elaborates
FAILED tests/conformance/test_predicate_unit_annotation.py::test_the_cured_predicate_is_a_working_gate
FAILED tests/conformance/test_predicate_unit_annotation.py::test_the_unit_is_not_resolved_as_a_reference
FAILED tests/conformance/test_predicate_unit_annotation.py::test_the_annotated_and_bare_twins_produce_identical_module_inputs
FAILED tests/conformance/test_predicate_unit_annotation.py::test_a_malformed_annotation_in_a_predicate_hard_refuses
FAILED tests/conformance/test_constraint_binding_unit_annotation.py::test_an_annotated_literal_binding_is_read_as_its_value
FAILED tests/conformance/test_constraint_binding_unit_annotation.py::test_an_annotated_reference_binding_is_read_as_a_reference
FAILED tests/conformance/test_constraint_binding_unit_annotation.py::test_neither_annotated_binding_is_refused_as_an_expression_source
FAILED tests/conformance/test_blocked_chain_diagnostic.py::test_the_detail_names_each_blocked_chain_as_authored
FAILED tests/conformance/test_blocked_chain_diagnostic.py::test_the_detail_states_the_bindings_rewrite
FAILED tests/conformance/test_blocked_chain_diagnostic.py::test_the_detail_names_the_source_location_by_basename
FAILED tests/conformance/test_blocked_chain_diagnostic.py::test_three_chain_occurrences_collapse_to_two_distinct_entries
FAILED tests/unit/test_render_block_reasons.py::test_a_present_location_renders_as_basename_and_line
FAILED tests/unit/test_render_block_reasons.py::test_an_absent_location_renders_no_suffix_at_all[no-location-fact]
FAILED tests/unit/test_render_block_reasons.py::test_an_absent_location_renders_no_suffix_at_all[empty-file]
FAILED tests/unit/test_render_block_reasons.py::test_an_absent_location_renders_no_suffix_at_all[no-line]
FAILED tests/unit/test_render_block_reasons.py::test_a_none_line_or_column_never_raises_at_sort_time
FAILED tests/unit/test_render_block_reasons.py::test_identical_diagnostics_collapse_to_one_entry
FAILED tests/unit/test_render_block_reasons.py::test_two_entries_differing_only_in_construct_order_stably
FAILED tests/unit/test_render_block_reasons.py::test_the_rendered_detail_is_one_line
========================= 20 failed, 6 passed in 0.46s =========================
```
