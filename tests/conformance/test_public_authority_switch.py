"""Slice 3E: every supported public caller constructs through the exact route.

What this module proves, and how it avoids proving it by spelling. A test that
asserts "the CLI imports ``build_exact_pipeline_context``" passes the moment the
import exists and says nothing about what the product does. Every assertion here
is a *behavioural* discriminator instead: a public artifact, or a public
refusal, that only one of the two authorities can produce.

Three discriminators carry the module:

- ``d38_caret`` ships different entry-point groups on the two routes — the exact
  route emits ``library_params`` with six parameters, the legacy route
  ``design_params`` with one. Generating it through the public CLI and reading
  the emitted ``inputs/*.json`` therefore names which authority built it.
- ``chain_spike_model`` is one of the twenty-two corpus fixtures the exact route
  refuses (``SI_SELF_BINDING``) and the legacy route generates. A public refusal
  is as much a product behaviour as a public package.
- A v5 snapshot is refused by name, and a snapshot this CLI captures is accepted
  by the same CLI's ``generate``.

The no-dual-authority checks are the other half: they enumerate the public
surface and fail if a second construction route, flag, or environment switch
appears.
"""

from __future__ import annotations

import ast
import json
import logging
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, main, run_codegen
from sysml_codegen.snapshot.envelope import SnapshotShapeError
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.legacy_route import generate_via_legacy_route

pytestmark = requires_license

CLI_SOURCE = Path(__import__("sysml_codegen.cli", fromlist=["cli"]).__file__)

#: The exact route resolves ``d38_caret``'s four modelled ``cell`` occurrences
#: and its exponent; the legacy route drops all five and attributes the one
#: entry point it keeps to ``design.sysml``. Measured, not chosen — see
#: ``test_exact_group_identity.py`` and diff-ledger row 12.
EXACT_D38_GROUP = "library_params"
LEGACY_D38_GROUP = "design_params"
EXACT_D38_PARAMETERS = {
    "D38Design__plant__noop__x",
    "D38Design__plant__pack__exponent",
    *(f"D38Design__plant__pack__cell[{index}]__base_cost" for index in range(4)),
}


def _input_payloads(package: Path) -> dict[str, dict[str, object]]:
    return {
        path.stem: json.loads(path.read_text())
        for path in sorted((package / "inputs").glob("*.json"))
    }


def _generate(models: Path, output: Path, **overrides: object) -> bool:
    config = GenerationConfig(
        models_path=models, output_path=output, package_name="switch_probe", **overrides
    )
    return run_codegen(config)


# ---------------------------------------------------------------------------
# (a) both public inputs construct through the exact route
# ---------------------------------------------------------------------------


def test_generate_from_models_ships_the_exact_routes_package(tmp_path: Path) -> None:
    """``generate --models`` emits the entry points only the exact route derives.

    The legacy route ships one ``design_params`` parameter for this model. If
    the switch had not landed, the file below would not exist and the assertion
    would name the legacy group instead.
    """
    output = tmp_path / "package"
    assert _generate(FIXTURES_DIR / "d38_caret", output) is True

    payloads = _input_payloads(output)
    assert set(payloads) == {EXACT_D38_GROUP}
    assert set(payloads[EXACT_D38_GROUP]) == EXACT_D38_PARAMETERS


def test_the_legacy_route_still_ships_its_own_answer_on_the_same_model(
    tmp_path: Path,
) -> None:
    """The discriminator above is a real one: the two routes genuinely differ.

    Without this arm the test above could be green because *both* routes emit
    ``library_params``. The legacy implementation is not deleted, so its answer
    is still measurable, and it is different.
    """
    output = tmp_path / "package"
    config = GenerationConfig(
        models_path=FIXTURES_DIR / "d38_caret", output_path=output, package_name="legacy_probe"
    )
    assert generate_via_legacy_route(config) is True

    payloads = _input_payloads(output)
    assert LEGACY_D38_GROUP in payloads
    assert set(payloads[LEGACY_D38_GROUP]) == {"D38Design__plant__noop__x"}


def test_generate_from_a_v6_snapshot_ships_the_same_exact_package(tmp_path: Path) -> None:
    """``generate --from-snapshot`` reaches the same authority as ``--models``.

    The snapshot is captured by this CLI's own ``snapshot`` subcommand, so the
    round trip also proves the two subcommands agree on a format.
    """
    snapshot = tmp_path / "d38.snapshot.json"
    main_returns(["snapshot", "--models", str(FIXTURES_DIR / "d38_caret"), "-o", str(snapshot)])

    output = tmp_path / "package"
    config = GenerationConfig(
        from_snapshot=snapshot, output_path=output, package_name="switch_probe"
    )
    assert run_codegen(config) is True

    payloads = _input_payloads(output)
    assert set(payloads) == {EXACT_D38_GROUP}
    assert set(payloads[EXACT_D38_GROUP]) == EXACT_D38_PARAMETERS


def test_generate_refuses_a_model_the_exact_route_rejects(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A public refusal is a public behaviour, and it is the exact route's.

    ``chain_spike_model`` is diff-ledger row 7: three self-named bindings the
    legacy route silently rescued and the exact route refuses. The second arm
    measures the legacy answer on the same model in the same test, so this is a
    route difference rather than a broken fixture.
    """
    output = tmp_path / "package"
    with caplog.at_level(logging.ERROR):
        assert _generate(FIXTURES_DIR / "chain_spike_model", output) is False
    assert "SI_SELF_BINDING" in caplog.text
    assert not output.exists()

    legacy_output = tmp_path / "legacy"
    legacy_config = GenerationConfig(
        models_path=FIXTURES_DIR / "chain_spike_model",
        output_path=legacy_output,
        package_name="legacy_probe",
    )
    assert generate_via_legacy_route(legacy_config) is True


# ---------------------------------------------------------------------------
# (b) no public surface selects between two authorities
# ---------------------------------------------------------------------------


def main_returns(argv: list[str]) -> None:
    """Run ``main`` with ``argv`` and require a zero exit."""
    import sys

    original = sys.argv
    sys.argv = ["sysml-codegen", *argv]
    try:
        main()
    except SystemExit as exit_code:
        assert exit_code.code == 0, f"{argv} exited {exit_code.code}"
    finally:
        sys.argv = original


#: Every module that owns a legacy construction authority. A public caller
#: reaching any of these is the dual authority this slice exists to close.
LEGACY_AUTHORITY_MODULES = frozenset(
    {
        "sysml_codegen.orchestration.pipeline_builder",
        "sysml_codegen.orchestration.snapshot_context",
        "sysml_codegen.snapshot.loader",
        "sysml_codegen.snapshot.graph_rebuild",
    }
)


def _imported_modules(source: Path) -> set[str]:
    """Every dotted module name the file imports, in any spelling."""
    tree = ast.parse(source.read_text())
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def test_the_cli_module_imports_no_legacy_construction_authority() -> None:
    """The shipped CLI cannot reach the legacy builders at all.

    Checked against every import spelling rather than one dotted string, the
    same widening Slice 3C's audit (F2) forced on the constraint-import pin.
    """
    assert _imported_modules(CLI_SOURCE) & LEGACY_AUTHORITY_MODULES == set()


def test_the_cli_names_exactly_one_construction_route() -> None:
    """``run_codegen`` builds a context one way, with no branch that selects an authority.

    The live and snapshot inputs are two *sources*, not two authorities: both
    seal into an ``ExactPipelineContext``. This pins that the only builders the
    CLI calls are the exact pair, so a re-added legacy fall-back fails here.
    """
    imported = _imported_modules(CLI_SOURCE)
    exact_builders = {
        name for name in imported if name.startswith("sysml_codegen.orchestration.exact_")
    }
    assert exact_builders == {
        "sysml_codegen.orchestration.exact_pipeline_context",
        "sysml_codegen.orchestration.exact_pipeline_context.build_exact_pipeline_context",
        "sysml_codegen.orchestration.exact_pipeline_context."
        "build_exact_pipeline_context_from_snapshot",
    }


def test_no_cli_flag_or_environment_variable_selects_a_route(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Enumerate the public flag surface and refuse a route-selecting escape hatch.

    ``--models`` and ``--from-snapshot`` select an input; nothing may select an
    implementation. The word list is deliberately broad so a flag named for the
    cutover cannot be added quietly.
    """
    forbidden = ("legacy", "exact", "route", "authority", "builder", "v5", "v6", "elaborat")
    for command in ("generate", "snapshot", "seal", "install-commands"):
        main_returns([command, "--help"])
        help_text = capsys.readouterr().out.lower()
        offenders = [word for word in forbidden if f"--{word}" in help_text]
        assert offenders == [], f"{command} exposes route-selecting flag(s) {offenders}"

    # Deliberately NOT `os.environ` — that would measure this pytest process, pass
    # spuriously for an operator who exports something unrelated, and keep passing
    # if run_codegen started reading SYSML_CODEGEN_ROUTE tomorrow. Pin the source.
    readers = sorted(
        name
        for name in _reachable_sysml_codegen_modules("sysml_codegen.cli")
        if _reads_the_environment(name)
    )
    assert readers == []


def test_the_public_api_exports_no_second_construction_entry_point() -> None:
    """``sysml_codegen.cli.__all__`` is the public API; pin it by value."""
    import sysml_codegen.cli as cli

    assert set(cli.__all__) == {
        "main",
        "run_codegen",
        "GenerationConfig",
        "cmd_generate",
        "cmd_install_commands",
        "CODEGEN_COMMANDS",
    }


def test_generation_config_carries_no_route_selector() -> None:
    """The public config object cannot express "use the other implementation"."""
    import dataclasses

    fields = {field.name for field in dataclasses.fields(GenerationConfig)}
    assert fields == {
        "output_path",
        "models_path",
        "from_snapshot",
        "package_name",
        "schema_class_name",
        "pipeline_name",
        "overwrite",
        "preserve_handwritten",
        "smart_regen",
    }


# ---------------------------------------------------------------------------
# (c) a v5 snapshot is refused by name, not silently accepted
# ---------------------------------------------------------------------------


def test_a_v5_snapshot_is_refused_by_name_at_the_loader() -> None:
    """The typed refusal names both the version found and the version required."""
    from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot

    v5 = FIXTURES_DIR / "fusion_tea" / "extraction_snapshot.json"
    assert json.loads(v5.read_text())["snapshot_format_version"] == 5

    with pytest.raises(SnapshotShapeError) as refusal:
        load_instance_graph_snapshot(v5)
    message = str(refusal.value)
    assert "v5" in message
    assert "v6" in message


def test_generate_from_a_v5_snapshot_refuses_without_falling_back(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """The CLI reports the refusal and writes nothing — no legacy fall-back, no traceback."""
    output = tmp_path / "package"
    config = GenerationConfig(
        from_snapshot=FIXTURES_DIR / "fusion_tea" / "extraction_snapshot.json",
        output_path=output,
        package_name="switch_probe",
    )
    with caplog.at_level(logging.ERROR):
        assert run_codegen(config) is False

    assert "v6" in caplog.text
    assert "Unexpected error" not in caplog.text
    assert "Traceback" not in caplog.text
    assert not output.exists()


def test_the_snapshot_subcommand_emits_what_generate_accepts(tmp_path: Path) -> None:
    """A CLI whose capture its own generate refuses would be self-inconsistent."""
    snapshot = tmp_path / "captured.json"
    main_returns(["snapshot", "--models", str(FIXTURES_DIR / "d38_caret"), "-o", str(snapshot)])

    document = json.loads(snapshot.read_text())
    assert document["version"] == 6
    assert "snapshot_format_version" not in document


# ---------------------------------------------------------------------------
# --design-path-filter: gone from the public surface (Gate 4B-G0, row L-025)
# ---------------------------------------------------------------------------


def test_design_path_filter_is_gone_from_the_public_surface(tmp_path: Path) -> None:
    """Slice 3E made the filter a typed refusal; Phase 4 removes the flag itself.

    The filter selected which design files the *legacy* parameter-group deriver
    read. The exact route derives groups from the instance graph, where it has no
    meaning, so there is nothing left to honour or to refuse — the argument is
    simply not one this CLI takes, and argparse says so before any model loads.
    """
    import sys

    assert not hasattr(GenerationConfig(output_path=tmp_path / "package"), "design_path_filter")

    original = sys.argv
    sys.argv = [
        "sysml-codegen",
        "generate",
        "--models",
        str(FIXTURES_DIR / "d38_caret"),
        "--output",
        str(tmp_path / "package"),
        "--design-path-filter",
        "designs",
    ]
    try:
        with pytest.raises(SystemExit) as exit_code:
            main()
    finally:
        sys.argv = original
    assert exit_code.value.code == 2  # argparse: unrecognized arguments
    assert not (tmp_path / "package").exists()


def test_the_snapshot_subcommand_takes_no_filter_either(tmp_path: Path) -> None:
    """Both subcommands lost it together; neither silently bakes one in."""
    import sys

    original = sys.argv
    sys.argv = [
        "sysml-codegen",
        "snapshot",
        "--models",
        str(FIXTURES_DIR / "d38_caret"),
        "-o",
        str(tmp_path / "s.json"),
        "--design-path-filter",
        "designs",
    ]
    try:
        with pytest.raises(SystemExit) as exit_code:
            main()
    finally:
        sys.argv = original
    assert exit_code.value.code == 2
    assert not (tmp_path / "s.json").exists()


# ---------------------------------------------------------------------------
# fail-before-mutate, re-pinned on the new authority (orchestrator ruling 5)
# ---------------------------------------------------------------------------


@pytest.fixture
def populated_output(tmp_path: Path) -> Path:
    """An output directory holding a file a failed run must not touch."""
    output = tmp_path / "package"
    (output / "handwritten").mkdir(parents=True)
    (output / "handwritten" / "keep_me.py").write_text("# hand-written, must survive\n")
    return output


def _tree(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_an_elaboration_refusal_leaves_an_existing_output_tree_untouched(
    populated_output: Path,
) -> None:
    """Refusal during context construction cannot reach the writer at all.

    This is the exact route's fail-before-mutate property, on a specimen the
    exact route actually refuses. The forged-source-identity specimen the legacy
    route used cannot serve here: the exact route resolves by declaration UUID,
    so a forged source identity does not produce a refusal for it to observe.
    """
    before = _tree(populated_output)
    config = GenerationConfig(
        models_path=FIXTURES_DIR / "chain_spike_model",
        output_path=populated_output,
        package_name="switch_probe",
        overwrite=True,
    )
    assert run_codegen(config) is False
    assert _tree(populated_output) == before


def test_a_refusal_after_the_context_but_before_the_writer_also_leaves_the_tree(
    populated_output: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The second guarded window: context built, refusal raised, nothing written.

    ``_check_duplicate_output_paths`` and ``_reconcile_params_coverage`` run
    after construction and before ``_clear_output_directory``. Injecting the
    refusal at that boundary is what proves the *ordering* rather than the
    fixture — the tree is only safe because no writer runs before those checks.
    """
    import sysml_codegen.cli as cli
    from sysml_codegen.generation import CodeGenerationError

    def refuse(_graph: object) -> None:
        raise CodeGenerationError("V11: injected params-coverage refusal")

    monkeypatch.setattr(cli, "_reconcile_params_coverage", refuse)

    before = _tree(populated_output)
    config = GenerationConfig(
        models_path=FIXTURES_DIR / "d38_caret",
        output_path=populated_output,
        package_name="switch_probe",
        overwrite=True,
    )
    assert run_codegen(config) is False
    assert _tree(populated_output) == before


def test_a_registry_class_name_collision_refuses_before_the_writer_runs(
    populated_output: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """The row-36 refusal, typed and ordered — the Slice 3E audit's F5, second half.

    ``unresolvable_attr_probe`` projects two formulas whose registry class names
    collide past the parent-segment alias. The guard that catches it lives at the
    registry pass, which runs *after* the output tree is cleared, and it raised a
    bare ``ValueError``: the operator saw "Unexpected error" with a traceback and
    kept a 34-file package with no contracts and no seal. Both halves are the
    subject here — the message is the package's own refusal, and the tree the run
    was pointed at is exactly as it was.
    """
    before = _tree(populated_output)
    config = GenerationConfig(
        models_path=FIXTURES_DIR / "unresolvable_attr_probe",
        output_path=populated_output,
        package_name="switch_probe",
        overwrite=True,
    )
    with caplog.at_level(logging.ERROR):
        assert run_codegen(config) is False
    assert "Code generation failed: Module class name collision survives aliasing" in caplog.text
    assert "Unexpected error" not in caplog.text
    assert _tree(populated_output) == before


def test_the_construction_path_reaches_no_legacy_authority_even_transitively() -> None:
    """The whole construction closure is clean, not just the CLI's own imports.

    This is also why the legacy forged-identity specimen is retired rather than
    ported. That specimen forged an ``IdentityFact`` on the neutral
    ``ConstraintFacts`` which ``analysis/constraint_lowering.py`` consumes, then
    monkeypatched ``build_pipeline_context`` to return the lowered result. Both
    halves live on modules nothing in this closure imports, so the exact route
    has no such refusal to observe. The fail-before-mutate responsibility moves
    to the two tests above; the specimen is repointed at the legacy route with a
    disposition row (recovery plan, Slice 3E test dispositions).
    """
    reachable = _reachable_sysml_codegen_modules(
        "sysml_codegen.orchestration.exact_pipeline_context"
    )
    assert "sysml_codegen.analysis.constraint_lowering" not in reachable
    assert LEGACY_AUTHORITY_MODULES & reachable == set()


def test_the_generation_half_still_reaches_v5_modules_and_that_residual_is_pinned() -> None:
    """State the limit honestly instead of implying the whole CLI is clean.

    ``sysml_codegen.cli``'s *transitive* closure still contains the legacy
    modules, because ``snapshot/__init__.py`` re-exports the v5 capture, loader
    and rebuild machinery and the CLI imports that package for other reasons.
    Nothing in that set is *constructed through* — the test above proves the
    construction closure is clean — but importable is importable, and a slice
    whose contract is that written claims survive checking should not round that
    down to zero.

    Pinned by name so the residual cannot quietly grow. Phase 4 empties it.
    """
    reachable = _reachable_sysml_codegen_modules("sysml_codegen.cli")
    assert LEGACY_AUTHORITY_MODULES & reachable == {
        "sysml_codegen.orchestration.pipeline_builder",
        "sysml_codegen.snapshot.loader",
        "sysml_codegen.snapshot.graph_rebuild",
    }


def _reads_the_environment(module_name: str) -> bool:
    """True if the module's source references ``os.environ`` or ``os.getenv``."""
    import importlib.util

    try:
        spec = importlib.util.find_spec(module_name)
    except (ImportError, AttributeError, ValueError):
        return False
    if spec is None or spec.origin is None or not spec.origin.endswith(".py"):
        return False
    source = Path(spec.origin).read_text()
    return "os.environ" in source or "os.getenv" in source or "getenv(" in source


def _reachable_sysml_codegen_modules(root: str) -> set[str]:
    """Every ``sysml_codegen`` module reachable by import from ``root``."""
    import importlib.util

    seen: set[str] = set()
    pending = [root]
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, AttributeError, ValueError):
            # ``_imported_modules`` also yields ``module.symbol`` spellings; a
            # symbol simply is not a module and contributes no further imports.
            continue
        if spec is None or spec.origin is None or not spec.origin.endswith(".py"):
            continue
        for imported in _imported_modules(Path(spec.origin)):
            if imported.startswith("sysml_codegen"):
                pending.append(imported)
    return seen
