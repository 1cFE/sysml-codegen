"""Real constraint verdict execution, through the public exact route, under real simkit.

This is the Gate 4C must-restore that `tests/execution/test_constraint_execution.py` and its
three siblings carried against the legacy route. Those files drive
`orchestration.pipeline_builder` and hand-assemble a `ComputationGraph` from
`analysis.constraint_lowering` and `analysis.parameter_groups` — three owners the retirement
deletes — so their evidence cannot survive it. What survives has to come from the surface a
user has: `run_codegen`, which since the Slice 3E authority switch *is* the exact route.

Every specimen here goes model → `run_codegen` → TEAx's own `ProvisionalPackageLoader` →
the real executor. Nothing constructs a graph, nothing patches an import, nothing reads a v5
snapshot. Verdicts are hand-derived from the models, never read back — each fixture's
`PROVENANCE.md` shows the arithmetic.

**How a value moves, and why not the way the legacy lane moved it.** The legacy tests edited a
generated `inputs/*.json` and re-ran. The exact route *seals* the package it writes, so that
edit is now a `SealVerificationError` — the plan calls the edit-and-reseal route invalid and
`test_editing_a_sealed_input_and_resealing_is_refused` proves the refusal is in code. The
ratified protocol is TEAx's typed entry injection: `CandidateBridge.build(selected_fields)`
fills every entry channel from the package's own modelled defaults and
`PreparedEvaluator.evaluate` runs the real executor against that mapping, with the seal an
active check throughout.

That gives two observation surfaces, and the specimens below use both deliberately:

- the **file-backed sealed run** publishes whole `ConstraintEvaluation` objects — status,
  `actual_value`, `margin`, `observed` — and persists `constraint_report.json`;
- **typed entry injection** is what can move a modelled value, and projects verdict
  *statuses* (`simkit/evaluation/projection.py`).

So a claim about the shape of a verdict is made against the first, and a claim about a value
driving a verdict is made against the second.

The responsibilities, one section each:

- both truth values, with the violated run completing rather than raising (INV-3);
- a non-finite operand reading as `indeterminate` rather than a confident verdict;
- the generated wrapper letting a native arithmetic failure propagate before evidence exists;
- polarity: one shared definition, two usages, opposite verdicts and opposite margin signs;
- the modelled actual really driving the verdict — usage-owned literal (Gate A), redefined
  actual (case 18), and sibling occurrence overrides (OD-A11).

Runs by hand in the agentic-mbse venv with `teax/packages/teax-simkit` on `sys.path`
(`tests/execution/conftest.py` documents the incantation); excluded from the default
`uv run pytest` via the `execution` marker.
"""

from __future__ import annotations

import importlib
import json
import math
from pathlib import Path

import pytest

from tests.execution.real_teax import (
    generate_package_from_models,
    load_sealed_package,
    package_loader,
)

pytestmark = pytest.mark.execution

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

REPORT_CH = "constraint_report"


def _generate(fixture: str, package_name: str, root: Path) -> Path:
    """Generate and seal one fixture through the shipped public route."""
    return generate_package_from_models(FIXTURES / fixture, root / package_name, package_name)


def _execute_from_files(package: Path, package_name: str, root: Path):
    """Seal-verify, import, and execute the package against its emitted input files."""
    from simkit.core.pipeline import execute_pipeline

    module, _fingerprint = load_sealed_package(package, package_name, root / "link_files")
    registry = getattr(module, f"create_{package_name}_registry")()
    return execute_pipeline(
        package / "pipelines" / "pipeline.yaml",
        root / "run_files",
        registry=registry,
        custom_schema_types=module.CUSTOM_SCHEMA_TYPES,
    )


def _entry_injector(package: Path, package_name: str, root: Path):
    """A callable that runs the sealed package with named entry points overridden.

    Injection, not mutation of the tree: the seal stays an active check because the same
    loader verifies the package the evaluator runs.
    """
    from simkit.evaluation.evaluator import PreparedEvaluator
    from simkit.study.bridge import CandidateBridge

    loader = package_loader(package, package_name, root / "link_injected")
    evaluator = PreparedEvaluator(loader, package / "pipelines" / "pipeline.yaml")
    bridge = CandidateBridge(evaluator.entry_models)

    def evaluate(selected_fields: dict[str, float]):
        return evaluator.evaluate(bridge.build(selected_fields))

    return evaluate


def _generated_inputs(package: Path) -> dict[str, float]:
    values: dict[str, float] = {}
    for input_file in sorted((package / "inputs").glob("*.json")):
        values.update(json.loads(input_file.read_text()))
    return values


def _generated_channels(package: Path) -> list[str]:
    """Every channel name the generated pipeline YAML declares, in file order."""
    import re

    yaml_text = (package / "pipelines" / "pipeline.yaml").read_text()
    return re.findall(r"[A-Za-z_][\w\[\]]*__evaluation\b", yaml_text)


def _sole_evaluation(result):
    """The one `ConstraintEvaluation` in a single-constraint package's report."""
    (evaluation,) = result.outputs[REPORT_CH].results
    return evaluation


def _verdicts(evidence) -> dict[str, str]:
    """Every per-constraint verdict status from an injected run, headline excluded."""
    return {name: status for name, status in evidence.responses.items() if name != "headline"}


# ---------------------------------------------------------------------------
# Both truth values
# ---------------------------------------------------------------------------


@pytest.mark.execution
def test_both_truth_values_and_the_violated_run_still_completes(tmp_path):
    """`gain >= threshold` on the Gate A usage-owned literal, satisfied then violated.

    `gain = 40.0` is declared on the concrete PartUsage `the_host` and read by a self-named
    actual; `threshold` takes its modelled default `10.0`. So the verdict is satisfied with
    margin `30.0`. Injecting `5.0` gives `5.0 >= 10.0` — violated — and that run must
    *complete* rather than raise (INV-3).

    Fixture `gate_a_d5`: `gate_a` itself is a ratified `expected-collapse` the exact route
    refuses, so this is its D-5 variant. The rename is the whole difference and the strip
    check in `tests/conformance/test_d5_variants.py` proves it.
    """
    name = "gate_a_verdicts"
    package = _generate("gate_a_d5", name, tmp_path)

    # The literal reached the generated inputs under its REAL qualified name. Before the
    # owner-classification fix, resolution asked for `GateA__the_host__viability__gain` — the
    # constraint's own QN as the root — and generation failed at the strict terminal miss.
    inputs = _generated_inputs(package)
    assert inputs["GateA__the_host__gain"] == 40.0
    assert inputs["GateA__the_host__viability__threshold"] == 10.0

    # The satisfied verdict, whole: status, truth value, margin, and what it observed.
    from_files = _execute_from_files(package, name, tmp_path)
    evaluation = _sole_evaluation(from_files)
    assert (evaluation.status, evaluation.actual_value, evaluation.margin) == (
        "satisfied",
        True,
        30.0,
    )
    assert evaluation.observed == {"gain_in": 40.0, "threshold": 10.0}
    # Ledger entry (expected-coverage.md, source-derived): 1 / 1 / 1 / 0 / 0 / {} / complete.
    # `model.sysml:57` declares the one usage, on the instantiated `part the_host : Host`.
    report = from_files.outputs[REPORT_CH]
    assert report.headline == "full_satisfaction"
    assert report.assessed_entry_count == 1
    assert report.coverage.model_dump() == {
        "authored_usage_total": 1,
        "applicable_gate_total": 1,
        "assessed_gate_count": 1,
        "unassessed_gate_count": 0,
        "inapplicable_gate_count": 0,
        "unassessed_reasons": {},
        "coverage_state": "complete",
    }

    # Persisted beside the ordinary outputs, not merely returned in process.
    (written_file,) = (tmp_path / "run_files").glob("*/constraint_report.json")
    assert json.loads(written_file.read_text())["results"][0]["status"] == "satisfied"

    # The other truth value, reached by moving the modelled literal.
    evaluate = _entry_injector(package, name, tmp_path)
    (constraint_id,) = _verdicts(evaluate({}))

    assert _verdicts(evaluate({}))[constraint_id] == "satisfied"
    violated = evaluate({"GateA__the_host__gain": 5.0})  # must NOT raise (INV-3)
    assert _verdicts(violated)[constraint_id] == "violated"
    assert violated.responses["headline"] == "violated"


# ---------------------------------------------------------------------------
# Indeterminate
# ---------------------------------------------------------------------------


@pytest.mark.execution
def test_a_non_finite_operand_reads_as_indeterminate_never_a_confident_verdict(tmp_path):
    """The exact failure the Kleene work exists to prevent.

    With `gain` non-finite there is no truth value to report, and the verdict must say so
    rather than answering `satisfied` because `inf >= 10.0` happens to evaluate. The headline
    has to carry it too: a run whose only constraint could not be assessed must not report
    itself as satisfied.
    """
    name = "gate_a_indeterminate"
    package = _generate("gate_a_d5", name, tmp_path)
    evaluate = _entry_injector(package, name, tmp_path)

    finite = evaluate({})
    (constraint_id,) = _verdicts(finite)
    assert _verdicts(finite)[constraint_id] == "satisfied"

    indeterminate = evaluate({"GateA__the_host__gain": math.inf})
    assert _verdicts(indeterminate)[constraint_id] == "indeterminate"
    assert indeterminate.responses["headline"] == "indeterminate"


# ---------------------------------------------------------------------------
# Arithmetic exception propagation
# ---------------------------------------------------------------------------


@pytest.mark.execution
def test_the_generated_wrapper_propagates_a_native_arithmetic_failure(tmp_path, monkeypatch):
    """The raise reaches the caller, and no evidence is constructed from a value that failed.

    `numerator_in / divisor_in <= bound_in` with `divisor_in = 0.0` raises inside the
    predicate. A wrapper that caught it and reported *anything* — violated, indeterminate, a
    zero margin — would publish a verdict about arithmetic that never happened. So the check
    is two-sided: the native `ZeroDivisionError` propagates, and `ConstraintEvaluation` is not
    constructed on the way out. The substitute below fails loudly if it is.
    """
    name = "arithmetic_raise_exec"
    package = _generate("constraint_arithmetic_raise", name, tmp_path)

    module, _fingerprint = load_sealed_package(package, name, tmp_path / "link_raise")
    wrapper_class = _sole_constraint_wrapper(module, name)

    def evidence_must_not_be_constructed(**_kwargs):
        raise AssertionError("ConstraintEvaluation was constructed after arithmetic failed")

    wrapper_module = importlib.import_module(wrapper_class.__module__)
    assert hasattr(wrapper_module, "ConstraintEvaluation"), (
        f"{wrapper_module.__name__} does not import ConstraintEvaluation; this test would "
        "otherwise pass without checking anything"
    )
    monkeypatch.setattr(wrapper_module, "ConstraintEvaluation", evidence_must_not_be_constructed)

    with pytest.raises(ZeroDivisionError) as error:
        wrapper_class().run(numerator_in=1.0, divisor_in=0.0, bound_in=10.0)
    assert str(error.value) == "float division by zero"


def _sole_constraint_wrapper(package_module, package_name: str) -> type:
    """The one generated constraint wrapper class in a single-constraint package.

    Taken from the package's own registry rather than by globbing its files, so a wrapper the
    package does not actually register cannot be picked up by mistake. The report aggregator
    is excluded by name: it is a constraint module, but it evaluates no predicate.
    """
    registry = getattr(package_module, f"create_{package_name}_registry")()
    keys = [
        key
        for key in registry.items()
        if key[0].endswith("ConstraintModule") and "Aggregator" not in key[0]
    ]
    assert len(keys) == 1, f"expected one constraint wrapper, found {[k for k, _ in keys]}"
    descriptor = keys[0][1]
    factory = descriptor.factory
    return factory if isinstance(factory, type) else type(factory())


# ---------------------------------------------------------------------------
# Polarity
# ---------------------------------------------------------------------------


@pytest.mark.execution
def test_one_shared_definition_two_polarities_two_verdicts(tmp_path):
    """Invariant 29 at execution: the margin sign comes from the usage, not the catalog order.

    `constraint_shared_polarity` types one `constraint def 'Within Bound'` twice off the same
    part: once plainly and once as `assert not constraint`. The predicate body is compiled
    once and is neutral (`m >= 0.0`), so both usages read the same raw value — and their
    verdicts and margin signs must nonetheless be opposites.

    `rating = 5.0` gives `m = 5.0 - 1.0 = 4.0`. Raw `4.0 >= 0.0` is True, margin `4.0`. The
    positive usage is satisfied at `+4.0`; the negated usage is violated at `-4.0`.
    """
    name = "shared_polarity_exec"
    package = _generate("constraint_shared_polarity", name, tmp_path)
    result = _execute_from_files(package, name, tmp_path)

    report = result.outputs[REPORT_CH]
    assert report.assessed_entry_count == 2
    assert report.headline == "violation"

    by_polarity = {
        "positive" if "pos_bound" in evaluation.constraint_id else "negative": evaluation
        for evaluation in report.results
    }
    assert set(by_polarity) == {"positive", "negative"}, [
        evaluation.constraint_id for evaluation in report.results
    ]

    # The same raw predicate value on both sides — one compiled body, read twice.
    assert by_polarity["positive"].actual_value is True
    assert by_polarity["negative"].actual_value is True

    assert (by_polarity["positive"].status, by_polarity["positive"].margin) == ("satisfied", 4.0)
    assert (by_polarity["negative"].status, by_polarity["negative"].margin) == ("violated", -4.0)

    # One neutral body, not one per usage.
    predicates = (package / "modules" / "constraints" / "predicates.py").read_text()
    assert predicates.count("def constraint_pred_") == 1


@pytest.mark.execution
@pytest.mark.parametrize(
    ("rating", "raw_value", "positive", "negative"),
    [
        (5.0, True, "satisfied", "violated"),
        (0.5, False, "violated", "satisfied"),
        (1.0, True, "satisfied", "violated"),
        (math.inf, None, "indeterminate", "indeterminate"),
    ],
    ids=["true", "false", "inclusive-boundary", "non-finite"],
)
def test_polarity_holds_at_every_boundary_of_the_shared_predicate(
    tmp_path, rating, raw_value, positive, negative
):
    """The two polarities stay opposites wherever the shared predicate lands.

    `m = rating - 1.0` against the neutral `m >= 0.0`. The interesting rows are the ones a
    single sample would miss: the raw-False direction, where the *negated* usage is the
    satisfied one; the inclusive boundary, where `>=` makes `m == 0.0` true so the negated
    usage is violated at a margin of zero rather than satisfied; and the non-finite operand,
    which is indeterminate on **both** sides — negating an unknown is still unknown, and a
    negated usage that answered `satisfied` there would be the Kleene bug wearing a different
    hat.
    """
    name = f"shared_polarity_{str(raw_value).lower()}_{str(rating).replace('.', '_')}"
    package = _generate("constraint_shared_polarity", name, tmp_path)
    evaluate = _entry_injector(package, name, tmp_path)
    rating_qn = "constraint_shared_polarity__the_design__h__rating"

    verdicts = _verdicts(evaluate({rating_qn: rating}))
    by_polarity = {
        "positive" if "pos_bound" in constraint_id else "negative": status
        for constraint_id, status in verdicts.items()
    }
    assert set(by_polarity) == {"positive", "negative"}, sorted(verdicts)
    assert by_polarity == {"positive": positive, "negative": negative}


@pytest.mark.execution
def test_the_strict_operator_disagrees_with_the_inclusive_one_at_the_boundary(tmp_path):
    """`m > 0.0` at exactly zero, where a `>` compiled as `>=` would still pass everywhere else.

    `constraint_strict_boundary` is `constraint_shared_polarity` with `>` instead of `>=`, and
    `rating = 1.0` puts `m` exactly on the boundary. The two fixtures must disagree there and
    agree nowhere else — a strict predicate is violated at equality where an inclusive one is
    satisfied, and the negated usages flip with them.
    """
    inclusive = _generate("constraint_shared_polarity", "boundary_inclusive", tmp_path)
    strict = _generate("constraint_strict_boundary", "boundary_strict", tmp_path)

    at_boundary = _verdicts(
        _entry_injector(inclusive, "boundary_inclusive", tmp_path / "inclusive")(
            {"constraint_shared_polarity__the_design__h__rating": 1.0}
        )
    )
    strict_at_boundary = _verdicts(
        _entry_injector(strict, "boundary_strict", tmp_path / "strict")(
            {"StrictBoundary__the_design__h__rating": 1.0}
        )
    )

    def by_polarity(verdicts: dict[str, str]) -> dict[str, str]:
        return {
            "positive" if "pos_bound" in constraint_id else "negative": status
            for constraint_id, status in verdicts.items()
        }

    assert by_polarity(at_boundary) == {"positive": "satisfied", "negative": "violated"}
    assert by_polarity(strict_at_boundary) == {"positive": "violated", "negative": "satisfied"}


# ---------------------------------------------------------------------------
# Multi-instance expansion
# ---------------------------------------------------------------------------


@pytest.mark.execution
def test_n_instances_produce_n_verdicts_from_one_compiled_predicate(tmp_path):
    """Compile-once at execution: three occurrences, three verdicts, one predicate body.

    `constraint_multi_instance` puts three `cell` occurrences under one design, each asserting
    the same definition. A predicate compiled per occurrence would still pass a verdict count
    check, so the two claims are made separately: the report carries three assessments, and
    the generated predicate module defines exactly one function.
    """
    name = "multi_instance_exec"
    package = _generate("constraint_multi_instance", name, tmp_path)

    # Three occurrences, three entry points, one per cell.
    inputs = _generated_inputs(package)
    assert sorted(inputs) == [
        f"constraint_multi_instance__the_design__c__cell[{index}]__cell_rating"
        for index in range(3)
    ]

    predicates = (package / "modules" / "constraints" / "predicates.py").read_text()
    assert predicates.count("def constraint_pred_") == 1

    report = _execute_from_files(package, name, tmp_path).outputs[REPORT_CH]
    # cell_rating 10.0 -> p = 20.0 >= 0.0 on all three.
    assert report.headline == "full_satisfaction"
    # The two-tier asymmetry, on a real package: `model.sysml:24` declares ONE usage, and
    # `part cell : Cell [3]` expands it to three occurrences. Ledger entry:
    # 1 / 1 / 1 / 0 / 0 / {} / complete, assessed_entry_count 3.
    assert report.assessed_entry_count == 3
    assert report.coverage.assessed_gate_count == 1
    assert report.coverage.applicable_gate_total == 1
    assert report.coverage.coverage_state == "complete"
    assert [evaluation.status for evaluation in report.results] == ["satisfied"] * 3


# ---------------------------------------------------------------------------
# Name safety, refused before execution
# ---------------------------------------------------------------------------


@pytest.mark.execution
def test_a_binding_that_collides_with_a_generated_name_is_refused_at_generation(
    tmp_path, caplog
):
    """R-3 closes before anything executes, and the refusal names the colliding binding.

    `constraint_inline` declares `value` on the host *and* binds a formal that generation
    would also render `value`. Emitting a package there would mean a predicate reading
    whichever `value` won, silently. The exact route refuses instead — from the live model,
    with no snapshot in the path.

    Observed the way a user observes it: `run_codegen` returns `False`, it says which binding
    collided, and it leaves **no** package behind. The last of those is the one that would
    matter if the refusal ever regressed into a warning.
    """
    import logging

    from sysml_codegen.cli import GenerationConfig, run_codegen

    output = tmp_path / "constraint_inline_refused"
    with caplog.at_level(logging.ERROR, logger="sysml_codegen.cli"):
        refused = run_codegen(
            GenerationConfig(
                models_path=FIXTURES / "constraint_inline",
                output_path=output,
                package_name="constraint_inline_refused",
                overwrite=True,
            )
        )

    assert refused is False
    assert "final_binding='value'" in caplog.text
    assert "collides with generated binding 'value'" in caplog.text
    assert not (output / "pipelines" / "pipeline.yaml").exists()


@pytest.mark.execution
def test_rewiring_the_generated_pipeline_is_caught_before_anything_executes(tmp_path):
    """INV-4 end to end, and the exact route catches it a step earlier than the legacy one.

    The legacy lane rewired an aggregator's input reference in an unsealed `pipeline.yaml`
    and required the *executor* to fail rather than silently skip the constraint. The exact
    route seals the package, so the same edit never reaches the executor: seal verification
    refuses the load and names the tampered file. Earlier and more specific — but only if the
    tamper is genuinely detected, so this makes the edit real and requires the refusal.
    """
    from simkit.evaluation.package_load import SealVerificationError

    name = "rewired_pipeline_exec"
    package = _generate("gate_a_d5", name, tmp_path)

    # A clean load first, so the refusal below cannot be a package that never loaded.
    load_sealed_package(package, name, tmp_path / "link_clean")

    yaml_path = package / "pipelines" / "pipeline.yaml"
    text = yaml_path.read_text()
    channel = next(
        name for name in _generated_channels(package) if name.endswith("__evaluation")
    )
    assert channel in text
    yaml_path.write_text(text.replace(channel, "nonexistent_evaluation_channel", 1))

    with pytest.raises(SealVerificationError) as refusal:
        load_sealed_package(package, name, tmp_path / "link_rewired")
    assert "pipelines/pipeline.yaml" in str(refusal.value)


# ---------------------------------------------------------------------------
# The modelled actual really drives the verdict
# ---------------------------------------------------------------------------


@pytest.mark.execution
def test_a_modeled_default_is_an_overridable_entry_point_not_a_baked_constant(tmp_path):
    """INV-6: the defaulted formal reaches the entry points and can flip the verdict.

    `threshold` has `default 10.0` on `constraint def 'Viability Threshold'`. If generation
    baked that into the compiled predicate, the constraint would still evaluate correctly at
    the default and nothing would ever notice. So the check is that the default arrives as a
    real entry point *and* that moving it changes the answer: at `10.0` the modelled
    `gain = 40.0` satisfies, at `60.0` it does not.
    """
    name = "modeled_default_exec"
    package = _generate("gate_a_d5", name, tmp_path)
    threshold_qn = "GateA__the_host__viability__threshold"

    assert _generated_inputs(package)[threshold_qn] == 10.0
    predicates = (package / "modules" / "constraints" / "predicates.py").read_text()
    assert "10.0" not in predicates, "the modelled default was baked into the predicate body"

    evaluate = _entry_injector(package, name, tmp_path)
    (constraint_id,) = _verdicts(evaluate({}))
    assert _verdicts(evaluate({}))[constraint_id] == "satisfied"
    assert _verdicts(evaluate({threshold_qn: 60.0}))[constraint_id] == "violated"


@pytest.mark.execution
def test_a_redefined_actual_drives_the_verdict(tmp_path):
    """Case 18: a definition-owned assert whose actual is redefined at the usage.

    `part def Panel` owns `assert constraint within : 'Within Limit' { in v = source.reading; }`
    and the redefining usage `part panel : Panel { :>> source.reading = 80.0; }` supplies the
    actual. Resolving it to a non-null design attribute is not the claim — Item 1's OD-R35
    lesson is that distinct wrappers can hide a collapsed value — so the redefined literal has
    to *move the verdict*. `80.0 <= 100.0` is satisfied; `120.0 <= 100.0` is violated.
    """
    name = "redefining_exec"
    package = _generate("constraint_def_owned_redefining", name, tmp_path)
    reading_qn = "constraint_def_owned_redefining__panel__source__reading"

    assert _generated_inputs(package)[reading_qn] == 80.0

    satisfied = _execute_from_files(package, name, tmp_path)
    evaluation = _sole_evaluation(satisfied)
    assert (evaluation.status, evaluation.actual_value) == ("satisfied", True)
    # Ledger entry: 1 / 1 / 1 / 0 / 0 / {} / complete — `model.sysml:27` is the one usage.
    assert satisfied.outputs[REPORT_CH].headline == "full_satisfaction"
    assert satisfied.outputs[REPORT_CH].coverage.coverage_state == "complete"

    evaluate = _entry_injector(package, name, tmp_path)
    (constraint_id,) = _verdicts(evaluate({}))
    assert _verdicts(evaluate({}))[constraint_id] == "satisfied"
    assert _verdicts(evaluate({reading_qn: 120.0}))[constraint_id] == "violated"


@pytest.mark.execution
def test_sibling_occurrence_overrides_reach_distinct_verdicts(tmp_path):
    """OD-A11: two instances of one part def, two literals, two different verdicts.

    Occurrence-stable usage identity is what keeps the siblings apart. Under the predecessor's
    nullable-QN membership, two anonymous-or-same-named sibling assertions could not be told
    apart and the route-counted demand sweep could collapse or duplicate their supplied
    values. Either failure shows up here as *matching* verdicts, which is why the assertion is
    on the pair rather than on each in isolation.

    `low` carries `:>> reading = 4.0` and `high` carries `6.0`, against `reading_in >= 5.0`.

    Fixture `constraint_occurrence_demand_overrides_d5`, whose two enumerated differences from
    the original — the D-5 rename and the model filename — are in its `PROVENANCE.md` and
    pinned in `tests/conformance/test_d5_variants.py`.
    """
    name = "occurrence_overrides_exec"
    package = _generate("constraint_occurrence_demand_overrides_d5", name, tmp_path)

    # The two siblings reach generation as distinct entry points with their own values.
    inputs = _generated_inputs(package)
    assert inputs["OccurrenceOverride__plant__low__reading"] == 4.0
    assert inputs["OccurrenceOverride__plant__high__reading"] == 6.0

    result = _execute_from_files(package, name, tmp_path)
    report = result.outputs[REPORT_CH]
    assert report.assessed_entry_count == 2
    assert report.headline == "violation"

    by_sibling = {
        "low" if "__low__" in evaluation.constraint_id else "high": evaluation
        for evaluation in report.results
    }
    assert set(by_sibling) == {"low", "high"}, [
        evaluation.constraint_id for evaluation in report.results
    ]
    assert (by_sibling["low"].status, by_sibling["low"].actual_value) == ("violated", False)
    assert (by_sibling["high"].status, by_sibling["high"].actual_value) == ("satisfied", True)
    assert by_sibling["low"].margin == -1.0
    assert by_sibling["high"].margin == 1.0

    # Persisted with both verdicts, so a collapse cannot hide behind an in-process object.
    (written_file,) = (tmp_path / "run_files").glob("*/constraint_report.json")
    written = json.loads(written_file.read_text())
    assert sorted(entry["status"] for entry in written["results"]) == ["satisfied", "violated"]
