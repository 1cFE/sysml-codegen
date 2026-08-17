"""A D-5 variant differs from its original by the rename and by nothing else.

The variants exist because the exact route refuses a binding that resolves to its own formal,
and the ratified migration for a real model is renaming. The risk in authoring one by hand is
not the rename — it is everything else that can ride along in a large diff: a reformat, a
dropped comment, a nudged literal. A reviewer reading two thousand lines will not catch it.

So the proof is mechanical and reversible: strip the ``_in`` suffix from the renamed formals
and the variant must reproduce its original **byte for byte, file for file**. That holds only
if the rename was the sole edit.

License-free by construction — it is a text comparison of committed fixtures.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import make_d5_variant as d5  # noqa: E402

#: Every variant, with the original it was derived from.
VARIANTS = [
    ("catf_mfe_model", "catf_mfe_d5"),
    ("solar_battery_model", "solar_battery_d5"),
    ("gate_a", "gate_a_d5"),
]


@pytest.fixture(scope="module")
def solar_graph():
    """The projected graph of the accepted variant. Licensed; built once."""
    from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
    from tests.conftest import requires_license  # noqa: F401 — marker lives on the nodes

    return build_elaborated_pipeline([d5.FIXTURES / "solar_battery_d5"])


def _module(graph, suffix: str):
    matches = [module for module in graph.modules if module.name.endswith(suffix)]
    assert len(matches) == 1, f"{suffix}: expected one module, found {len(matches)}"
    return matches[0]


def _entry_point_values(graph) -> dict[str, float]:
    """Every entry point's value by qualified name — library defaults and design attributes."""
    return {
        parameter.qualified_name: parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }


def _evaluate(graph, module) -> dict[str, float]:
    """Run the module's own compiled expressions, in order, on the graph's entry-point values.

    Seeding from the graph rather than from the module's inline defaults is deliberate: it
    makes the design attributes (`racking.panel_count = 20.0`) part of what is checked, so a
    design value that failed to reach the graph fails here instead of quietly defaulting.
    """
    values = _entry_point_values(graph)
    scope = {}
    for i in module.inputs:
        if str(i.source.source_type).endswith("entry_point"):
            scope[i.param_name] = values[i.source.qualified_name]
    for expression in module.calc_expressions:
        if "=" not in expression or expression.lstrip().startswith("\n"):
            continue
        name, _, body = expression.partition("=")
        scope[name.strip()] = eval(body.strip(), {"__builtins__": {}}, scope)  # noqa: S307
    return scope


@pytest.mark.parametrize(("original", "variant"), VARIANTS)
def test_stripping_the_rename_reproduces_the_original_byte_for_byte(
    original: str, variant: str
) -> None:
    assert d5.strip_check(original, variant, d5.refused_formals(original)) == []


@pytest.mark.parametrize(("original", "variant"), VARIANTS)
def test_the_variant_renames_every_formal_the_route_refused(
    original: str, variant: str
) -> None:
    """No partial migration: a formal left un-renamed would still refuse, silently."""
    text = "".join(
        path.read_text() for path in sorted((d5.FIXTURES / variant).rglob("*.sysml"))
    )
    for formal in d5.refused_formals(original):
        assert f"{formal}_in" in text, f"{variant}: {formal} was not renamed"


@pytest.mark.parametrize(("original", "variant"), VARIANTS)
def test_a_variant_carries_no_v5_snapshot(original: str, variant: str) -> None:
    """The v5 snapshot has not come back, here or anywhere under fixtures.

    Corpus membership used to mean exactly this file's presence, and a variant is not a
    corpus fixture. The file retired with the v5 family (retirement step 2), so the node
    now says the stronger and still-checkable thing: no fixture carries one. Its own v6
    snapshot is fine and in fact wanted — that is what lets a repointed test read the
    variant's graph without a licence.
    """
    assert not (d5.FIXTURES / variant / d5.RETIRED_CORPUS_MARKER).exists()
    assert list(d5.FIXTURES.rglob(d5.RETIRED_CORPUS_MARKER)) == []


@pytest.mark.parametrize(("original", "variant"), VARIANTS)
def test_the_original_is_untouched_by_its_variant(original: str, variant: str) -> None:
    """The corpus guarantee: the refused original still carries the refused shape."""
    text = "".join(
        path.read_text() for path in sorted((d5.FIXTURES / original).rglob("*.sysml"))
    )
    for formal in d5.refused_formals(original):
        assert f"{formal}_in" not in text, f"{original} was edited in place"
    # The original's committed `extraction_snapshot.json` used to be asserted here as the
    # second half of "untouched" — the variant copier excludes it by name, so its presence
    # in the original proved the copy had not moved it. It retired with the v5 family
    # (retirement step 2), and these three originals carry no v6 capture of their own, so
    # there is no file left to make that statement about. The SysML text above is the whole
    # check now.


#: The occurrence-overrides variant, which the parametrized set above cannot carry: it has no
#: batch record (so `refused_formals` has nothing to read), and it differs from its original by
#: one filename as well as by the rename. Both differences are enumerated in its PROVENANCE.md.
OVERRIDES_ORIGINAL = d5.FIXTURES / "constraint_occurrence_demand" / "overrides" / "model.sysml"
OVERRIDES_VARIANT = (
    d5.FIXTURES / "constraint_occurrence_demand_overrides_d5" / "occurrence_overrides.sysml"
)


def test_the_occurrence_overrides_variant_differs_by_the_rename_and_the_filename() -> None:
    """Two enumerated differences, and the byte comparison catches a third if one rode along.

    The file is named rather than left as ``model.sysml`` because the exact route refuses a
    package-scoped calc in a ``model.sysml`` — parameter-group identity comes from the filename
    stem, and the fallback wants an owning root occurrence a package-scoped calc does not have
    (Slice 3B orchestrator ruling, option C). That is a rename of the file, not of its contents:
    stripping ``_in`` must still reproduce the original's bytes exactly.
    """
    import re as _re

    assert not (OVERRIDES_VARIANT.parent / "model.sysml").exists(), (
        "the variant carries both names; the filename difference is supposed to be a rename"
    )
    stripped = _re.sub(r"\breading_in\b", "reading", OVERRIDES_VARIANT.read_text())
    assert stripped.encode() == OVERRIDES_ORIGINAL.read_bytes()


def test_the_occurrence_overrides_original_is_untouched() -> None:
    """The original still carries the refused self-binding shape."""
    assert "in reading = reading;" in OVERRIDES_ORIGINAL.read_text()
    assert "reading_in" not in OVERRIDES_ORIGINAL.read_text()


def test_a_refusal_code_outside_the_rename_recipe_stops_rather_than_guesses() -> None:
    """The recipe addresses SI_SELF_BINDING. Anything else is a finding, not a variant."""
    import json

    manifest = json.loads(d5.BATCH_MANIFEST.read_text())
    for original, _variant in VARIANTS:
        codes = set(manifest["records"][original]["codes"])
        assert codes == {"SI_SELF_BINDING"}, (
            f"{original} carries {sorted(codes - {'SI_SELF_BINDING'})}, which the D-5 "
            "recipe does not address — make_d5_variant.py must stop rather than emit"
        )


# --- Stage 2: the aggregation split ------------------------------------------
#
# The committed D-5 variant retains one named attribute per term. Those intermediates remain a
# useful authored shape, but R8 no longer requires them to distinguish same-leaf source families.
# A shape change cannot be proved by stripping a suffix, so these pin the summands, hand-derived
# numbers, and the stage-one graph that now succeeds without the split.

SOLAR = "solar_battery_d5"

#: Site Infrastructure, hand-computed from the model. See the fixture's PROVENANCE.md.
RACKING_MATERIAL = 20.0 * 57.0
RACKING_FABRICATION = RACKING_MATERIAL * 0.45
RACKING_INSTALLATION = RACKING_MATERIAL * 0.30
RACKING_TOTAL = RACKING_MATERIAL + RACKING_FABRICATION + RACKING_INSTALLATION
PANEL_MATERIAL = 150.0 + 4.0 * 34.0
PANEL_FABRICATION = PANEL_MATERIAL * 0.45
PANEL_INSTALLATION = PANEL_MATERIAL * 0.30
PANEL_TOTAL = PANEL_MATERIAL + PANEL_FABRICATION + PANEL_INSTALLATION
PERMITTING_TOTAL = 8.0 * 187.5

SITE_CAPITAL = RACKING_TOTAL + PANEL_TOTAL + PERMITTING_TOTAL
SITE_MATERIAL = RACKING_MATERIAL + PANEL_MATERIAL + 0.0


def test_the_aggregation_split_changed_no_summand() -> None:
    """Semantic equivalence: each rewritten rollup adds exactly what it added before."""
    original = (d5.FIXTURES / "solar_battery_model" / "library.sysml").read_text()
    variant = (d5.FIXTURES / SOLAR / "library.sysml").read_text()
    before = d5.aggregation_rewrites(original)
    assert before, "no colliding rollup found in the original — the fixture changed"

    added = {
        line.strip().split()[1]: line.split("=", 1)[1].strip().rstrip(";").strip()
        for rewrite in d5.aggregation_rewrites(_renamed(original))
        for line in rewrite["added"]
    }
    for rewrite in before:
        stripped = [_strip_suffix(term) for term in rewrite["terms"]]
        assert sorted(stripped) == sorted(rewrite["terms"]), "renaming touched a rollup term"
    for name, expression in added.items():
        assert f"attribute {name} : Real = {expression};" in variant, (
            f"{name} is enumerated but not present as authored"
        )


def _strip_suffix(term: str) -> str:
    import re as _re

    return _re.sub(r"_in\b", "", term)


def _renamed(text: str) -> str:
    """Stage-1 output for one file, rebuilt in memory — never written to the tree."""
    import re as _re

    for name in d5.refused_formals("solar_battery_model"):
        for span in sorted(d5._definition_blocks(text).values(), reverse=True):
            if _re.search(rf"\bin\s+attribute\s+{_re.escape(name)}\b", text[span[0] : span[1]]):
                text = d5._rename_in_span(text, span, name)
        text = d5._rename_binding_left_sides(text, name)
    return text


def test_the_enumerated_list_matches_what_the_readme_publishes() -> None:
    """A list nobody can check is not an enumeration."""
    readme = (d5.FIXTURES / SOLAR / "PROVENANCE.md").read_text()
    rewrites = d5.aggregation_rewrites(
        _renamed((d5.FIXTURES / "solar_battery_model" / "library.sysml").read_text())
    )
    assert f"{len(rewrites)} rollups rewritten" in readme
    for rewrite in rewrites:
        for line in rewrite["added"]:
            assert f"`{line.strip().split()[1]}`" in readme, "an added attribute is unpublished"


def _stage_one_only(destination: Path) -> Path:
    """A copy of solar_battery_model with the renames and nothing else."""
    import shutil

    root = destination / "solar_stage_one"
    shutil.copytree(
        d5.FIXTURES / "solar_battery_model",
        root,
        ignore=lambda _d, names: {n for n in names if n in d5.NOT_INHERITED},
    )
    for file in sorted(root.rglob("*.sysml")):
        file.write_text(_renamed(file.read_text()))
    return root


def test_the_rename_alone_preserves_distinct_same_leaf_source_families(
    tmp_path: Path,
) -> None:
    """The stage-one model projects every same-leaf role without the authored split."""
    from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline

    graph = build_elaborated_pipeline([_stage_one_only(tmp_path)])
    rollup = _module(graph, "solar_array__raw_material_cost")
    source_by_parameter = {
        item.param_name: item.source.producer_channel for item in rollup.inputs
    }

    plant = "SolarBatteryDesign__solar_battery_plant__solar_array"
    assert {
        name for name in source_by_parameter if name.startswith("pv_module_raw_material_cost_")
    } == {f"pv_module_raw_material_cost_{index}" for index in range(20)}
    assert {
        source
        for name, source in source_by_parameter.items()
        if name.startswith("pv_module_raw_material_cost_")
    } == {
        f"{plant}__pv_module[{index}]__cost_model__material_cost" for index in range(20)
    }
    assert {
        name for name in source_by_parameter if name.startswith("inverter_raw_material_cost_")
    } == {f"inverter_raw_material_cost_{index}" for index in range(4)}
    assert {
        source
        for name, source in source_by_parameter.items()
        if name.startswith("inverter_raw_material_cost_")
    } == {
        f"{plant}__inverter[{index}]__cost_model__material_cost" for index in range(4)
    }
    assert source_by_parameter["array_bos_raw_material_cost"] == (
        f"{plant}__array_bos__cost_model__material_cost"
    )


def test_the_variant_projects_the_site_infrastructure_arithmetic_by_hand(
    solar_graph,
) -> None:
    """Numbers derived from the model, never copied from a route's output."""
    leaves = {
        "racking": (RACKING_MATERIAL, RACKING_FABRICATION, RACKING_INSTALLATION, RACKING_TOTAL),
        "electrical_panel": (PANEL_MATERIAL, PANEL_FABRICATION, PANEL_INSTALLATION, PANEL_TOTAL),
    }
    for child, expected in leaves.items():
        module = _module(solar_graph, f"site_infra__{child}__cost_model")
        values = _evaluate(solar_graph, module)
        assert values["material_cost"] == expected[0]
        assert values["fab_cost"] == expected[1]
        assert values["install_cost"] == expected[2]
        assert values["total_cost"] == expected[3]

    permitting = _evaluate(
        solar_graph, _module(solar_graph, "site_infra__permitting__cost_model")
    )
    assert permitting["total_cost"] == PERMITTING_TOTAL
    assert permitting["material_cost"] == 0.0


def test_each_rollup_reads_one_named_intermediate_per_child(solar_graph) -> None:
    """The point of the split: three distinct parameters, three distinct sources."""
    expected = {
        "capital_cost": ("total_cost", True),
        "raw_material_cost": ("material_cost", False),
        "fabrication_cost": ("fab_cost", False),
        "installation_cost": ("install_cost", False),
    }
    for metric, (channel_suffix, permitting_is_wired) in expected.items():
        module = _module(solar_graph, f"site_infra__{metric}")
        inputs = {i.param_name: i.source for i in module.inputs}
        assert set(inputs) == {
            f"racking_{metric}",
            f"electrical_panel_{metric}",
            f"permitting_{metric}",
        }, f"{metric}: the rollup does not read one named intermediate per child"
        for child in ("racking", "electrical_panel"):
            channel = inputs[f"{child}_{metric}"].producer_channel
            assert channel is not None and channel.endswith(
                f"{child}__cost_model__{channel_suffix}"
            ), f"{metric}: {child} is wired to {channel}"
        source = inputs[f"permitting_{metric}"]
        if permitting_is_wired:
            assert source.producer_channel is not None
        else:
            # `:>> raw_material_cost = 0.0;` on Permitting is a literal, so it is an
            # entry point rather than a produced channel. That is the model, not a gap.
            assert source.producer_channel is None


# --- Phase 2 (self-binding-replacement): external-root customer mode ----------
#
# The customer migration operates on an external tree that keeps TWO synchronized
# model sets. The vendored `fusion_tea` fixture is the already-migrated worked
# target, so the simulation is a closed loop: strip the `_in` renames to
# reconstruct the pre-migration customer shape, duplicate it into both sets, run
# the tool, and require the result to reproduce the vendored fixture byte for
# byte. Nothing here reads /home/reid/1cfe/fusion-tea.

#: The 11 renamed formals, per Appendix A of the design.
EXPECTED_FORMALS = sorted(
    [
        "availability",
        "beam_energy_mj",
        "discount_rate",
        "frequency",
        "gain",
        "net_electric_power_gw",
        "num_chambers",
        "om_cost_constant",
        "plant_cost_constant",
        "thermal_efficiency",
        "thermal_power_gw",
    ]
)

#: The six logical model files that carry the 30 rewritten rows per set.
MIGRATED_FILES = [
    "designs/generic_ife/ife_plant.sysml",
    "designs/hif_ife/hif_driver.sysml",
    "designs/hif_ife/hif_plant.sysml",
    "library/analyses/fusion_cycle.sysml",
    "library/analyses/hif_economics.sysml",
    "library/analyses/ife_lcoe.sysml",
]

#: The two synchronized customer model sets (design D12 / bet B8).
MODEL_SETS = ["models", "exploration/ife_e2e/models"]


def _stripped(text: str) -> str:
    """The pre-migration customer shape: every D-5 rename undone."""
    for name in EXPECTED_FORMALS:
        text = re.sub(rf"\b{re.escape(name)}_in\b", name, text)
    return text


def _customer_tree(destination: Path) -> Path:
    """A dual-set pre-migration customer simulation built from the vendored fixture."""
    root = destination / "customer"
    sources = sorted((d5.FIXTURES / "fusion_tea").rglob("*.sysml"))
    assert sources, "the vendored fusion_tea fixture has no model files"
    for prefix in MODEL_SETS:
        for source in sources:
            relative = source.relative_to(d5.FIXTURES / "fusion_tea")
            target = root / prefix / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(_stripped(source.read_text()))
    return root


def _tree_digest(root: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_external_dual_tree_migration_reproduces_the_vendored_fixture(
    tmp_path: Path,
) -> None:
    """The closed loop: preconditions clear, the strip check is reversible, both
    sets receive the identical migration, and every migrated file equals the
    already-migrated vendored fixture byte for byte. The originals never move."""
    root = _customer_tree(tmp_path)
    before = _tree_digest(root)
    scratch = tmp_path / "scratch"

    assert d5.precondition_findings(root, EXPECTED_FORMALS) == []
    d5.build_variant_tree(root, scratch, EXPECTED_FORMALS)
    assert d5.strip_check_tree(root, scratch, EXPECTED_FORMALS) == []

    for prefix in MODEL_SETS:
        for relative in MIGRATED_FILES:
            variant = (scratch / prefix / relative).read_bytes()
            vendored = (d5.FIXTURES / "fusion_tea" / relative).read_bytes()
            assert variant == vendored, f"{prefix}/{relative} diverges from the fixture"

    first, second = MODEL_SETS
    for relative in sorted(
        path.relative_to(scratch / first)
        for path in (scratch / first).rglob("*.sysml")
    ):
        assert (scratch / first / relative).read_bytes() == (
            scratch / second / relative
        ).read_bytes(), f"the two migrated sets diverge at {relative}"

    assert _tree_digest(root) == before, "the customer originals were touched"


def test_migration_rewrites_the_thirty_census_rows_per_model_set(tmp_path: Path) -> None:
    """The D12 census rows: 15 binding left sides + 15 formal declarations per
    set. Expression uses inside the declaring blocks rename with their formal
    (the recipe renames every code use), so the per-line guarantee is reversal:
    every changed line differs from its original by `_in` insertions alone."""
    root = _customer_tree(tmp_path)
    scratch = tmp_path / "scratch"
    d5.build_variant_tree(root, scratch, EXPECTED_FORMALS)

    for prefix in MODEL_SETS:
        changed = []
        binding_rows = declaration_rows = 0
        for relative in MIGRATED_FILES:
            original_lines = (root / prefix / relative).read_text().splitlines()
            variant_lines = (scratch / prefix / relative).read_text().splitlines()
            assert len(original_lines) == len(variant_lines), relative
            changed.extend(
                (before_line, line)
                for before_line, line in zip(original_lines, variant_lines)
                if before_line != line
            )
        for before_line, line in changed:
            assert _stripped(line) == before_line, (
                f"{prefix}: changed line is not rename-only: {line!r}"
            )
            if re.search(r"\bin\s+\w+_in\s*=", line):
                binding_rows += 1
            if re.search(r"\battribute\s+\w+_in\b", line):
                declaration_rows += 1
        assert binding_rows == 15, f"{prefix}: {binding_rows} binding rows"
        assert declaration_rows == 15, f"{prefix}: {declaration_rows} declaration rows"


def test_discovery_enumerates_every_customer_site(tmp_path: Path) -> None:
    """The census is explicit output, not a side effect: 30 binding sites and 30
    declaration blocks across the two sets, each named by file and line."""
    root = _customer_tree(tmp_path)
    sites = d5.discover_sites(root, EXPECTED_FORMALS)
    assert set(sites) == set(EXPECTED_FORMALS)
    bindings = [site for record in sites.values() for site in record["bindings"]]
    declarations = [site for record in sites.values() for site in record["declarations"]]
    assert len(bindings) == 30
    assert len(declarations) == 30
    for site in bindings + declarations:
        path, _, line = site.rpartition(":")
        assert line.isdigit(), site
        assert (root / path).is_file(), site


def _hazard_tree(destination: Path, library: str, design: str | None = None) -> Path:
    root = destination / "hazard"
    (root / "library").mkdir(parents=True)
    (root / "library" / "model.sysml").write_text(library)
    if design is not None:
        (root / "designs").mkdir(parents=True)
        (root / "designs" / "design.sysml").write_text(design)
    return root


def _refuses_without_writing(root: Path, formals: list[str], tag: str, tmp_path: Path) -> None:
    """Every hazard refuses at precondition time, exits 1, and writes nothing."""
    before = _tree_digest(root)
    findings = d5.precondition_findings(root, formals)
    assert any(finding.startswith(tag) for finding in findings), findings

    scratch = tmp_path / "hazard_scratch"
    rc = d5.main(
        ["--root", str(root), "--scratch", str(scratch), "--formals", ",".join(formals)]
    )
    assert rc == 1
    assert not scratch.exists(), "a refused run must not create the scratch tree"
    assert _tree_digest(root) == before, "a refused run must leave the tree unchanged"


def test_precondition_a_sibling_member_of_the_bare_name_stops(tmp_path: Path) -> None:
    """D5(a): the declaring definition carries another member of the bare name,
    so the block-wide rename would mint duplicate `<name>_in` members — the
    s5/s7 collision family — instead of freeing the bare reference."""
    root = _hazard_tree(
        tmp_path,
        """package HazardSibling {
    private import ScalarValues::*;

    calc def Revenue {
        in attribute gain : Real;
        out attribute gain : Real = gain * 2.0;
    }

    part def Plant {
        attribute gain : Real = 1.0;
        calc revenue_calc : Revenue { in gain = gain; }
    }

    part plant : Plant;
}
""",
    )
    _refuses_without_writing(root, ["gain"], "(a)", tmp_path)


def test_precondition_b_existing_target_name_stops(tmp_path: Path) -> None:
    """D5(b): `<name>_in` already exists in the tree, so the rename would
    collide with (or silently capture) an existing member."""
    root = _hazard_tree(
        tmp_path,
        """package HazardTaken {
    private import ScalarValues::*;

    calc def Revenue {
        in attribute gain : Real;
        out attribute revenue : Real = gain * 2.0;
    }

    part def Plant {
        attribute gain : Real = 1.0;
        attribute gain_in : Real = 3.0;
        calc revenue_calc : Revenue { in gain = gain; }
    }

    part plant : Plant;
}
""",
    )
    _refuses_without_writing(root, ["gain"], "(b)", tmp_path)


def test_precondition_c_unrelated_same_named_left_side_stops(tmp_path: Path) -> None:
    """D5(c) / B7: an `in gain =` left side belongs to a usage whose type is not
    a definition being renamed (here: not declared anywhere in the tree), so the
    file-wide left-side rewrite would break a binding outside the migration."""
    root = _hazard_tree(
        tmp_path,
        """package HazardForeign {
    private import ScalarValues::*;

    calc def Revenue {
        in attribute gain : Real;
        out attribute revenue : Real = gain * 2.0;
    }

    part def Plant {
        attribute gain : Real = 1.0;
        calc revenue_calc : Revenue { in gain = gain; }
        calc foreign_calc : 'External Model' { in gain = gain; }
    }

    part plant : Plant;
}
""",
    )
    _refuses_without_writing(root, ["gain"], "(c)", tmp_path)


def test_precondition_d_live_rollup_stops(tmp_path: Path) -> None:
    """D5(d) / B6: `aggregation_rewrites` matches a rollup, so the tool's second
    transformation would fire — a shape change the strip check cannot see. The
    run refuses instead of rewriting customer physics."""
    root = _hazard_tree(
        tmp_path,
        """package HazardRollup {
    private import ScalarValues::*;

    calc def Revenue {
        in attribute gain : Real;
        out attribute revenue : Real = gain * 2.0;
    }

    part def Assembly {
        attribute total : Real;
        attribute gain : Real = 1.0;
        calc revenue_calc : Revenue { in gain = gain; }
    }

    part asm : Assembly {
        :>> total =
            sum(pv.cost) + sum(inverter.cost);
    }
}
""",
    )
    _refuses_without_writing(root, ["gain"], "(d)", tmp_path)


def test_cli_root_mode_runs_the_whole_customer_pipeline(
    tmp_path: Path, capsys
) -> None:
    """One command: discovery output, clear preconditions, scratch build, strip
    check — exit 0 and the printed census names the counts an operator reviews."""
    root = _customer_tree(tmp_path)
    scratch = tmp_path / "scratch"

    rc = d5.main(
        ["--root", str(root), "--scratch", str(scratch), "--formals", ",".join(EXPECTED_FORMALS)]
    )
    captured = capsys.readouterr().out
    assert rc == 0
    assert scratch.is_dir()
    assert "30 binding sites" in captured
    assert "30 declaration blocks" in captured
    assert "preconditions: clear" in captured
    assert "strip check: 0 problems" in captured


def test_cli_root_mode_requires_explicit_formals(tmp_path: Path) -> None:
    """An external tree has no batch record, so the formals must be a stated
    caller decision — never guessed."""
    root = _customer_tree(tmp_path)
    with pytest.raises(SystemExit):
        d5.main(["--root", str(root), "--scratch", str(tmp_path / "scratch")])


# --- Audit F3 (self-binding-replacement): destructive-path and lookup guards ---
#
# Customer mode deletes its scratch destination before building. An aliased or
# overlapping source/scratch pair would therefore destroy the input tree, and a
# pre-existing scratch directory would be deleted without ever having been this
# run's output. Every unsafe relationship must refuse before any deletion, with
# the customer tree byte-identical afterward.


def _refused_path_pair(root: Path, scratch: str | Path) -> None:
    before = _tree_digest(root)
    rc = d5.main(
        ["--root", str(root), "--scratch", str(scratch), "--formals", "gain"]
    )
    assert rc == 1
    assert _tree_digest(root) == before, "a refused run must leave the tree unchanged"


def test_customer_mode_refuses_scratch_equal_to_root(tmp_path: Path) -> None:
    root = _customer_tree(tmp_path)
    _refused_path_pair(root, root)


def test_customer_mode_refuses_scratch_inside_root(tmp_path: Path) -> None:
    root = _customer_tree(tmp_path)
    _refused_path_pair(root, root / "models" / "scratch")


def test_customer_mode_refuses_root_inside_scratch(tmp_path: Path) -> None:
    """The reverse nesting: deleting the scratch would recurse into the root."""
    root = _customer_tree(tmp_path)
    _refused_path_pair(root, tmp_path)


def test_customer_mode_refuses_a_pre_existing_scratch_target(tmp_path: Path) -> None:
    """A directory that already exists is not this run's output; deleting it would
    destroy someone else's bytes. Build mode refuses; --check requires it instead."""
    root = _customer_tree(tmp_path)
    scratch = tmp_path / "already_there"
    scratch.mkdir()
    sentinel = scratch / "keep.txt"
    sentinel.write_bytes(b"not yours to delete\n")

    _refused_path_pair(root, scratch)
    assert sentinel.read_bytes() == b"not yours to delete\n"


def test_check_mode_requires_an_existing_scratch(tmp_path: Path) -> None:
    root = _customer_tree(tmp_path)
    rc = d5.main(
        [
            "--root",
            str(root),
            "--scratch",
            str(tmp_path / "never_built"),
            "--formals",
            "gain",
            "--check",
        ]
    )
    assert rc == 1


def _fixture_mode_sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    fixtures = tmp_path / "fixtures"
    source = fixtures / "source"
    source.mkdir(parents=True)
    (source / "model.sysml").write_text("package p {}\n")
    monkeypatch.setattr(d5, "FIXTURES", fixtures)
    return fixtures


def test_fixture_mode_refuses_escaped_operands_with_exit_one_and_no_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Absolute, traversal, aliased, and missing operands all refuse before write."""
    fixtures = _fixture_mode_sandbox(tmp_path, monkeypatch)
    external = tmp_path / "external"
    external.mkdir()
    (external / "keep.txt").write_bytes(b"not a fixture\n")
    (fixtures / "escaped").symlink_to(external, target_is_directory=True)
    (fixtures / "alias").symlink_to(fixtures / "source", target_is_directory=True)

    for argv in (
        ["source", str(external)],
        [str(external), "fresh"],
        ["source", "../escape"],
        ["../source", "fresh"],
        ["source", "source"],
        ["source", "alias"],
        ["source", "escaped"],
        ["missing", "fresh"],
    ):
        before = _tree_digest(tmp_path)
        assert d5.main([*argv, "--formals", "gain"]) == 1
        assert _tree_digest(tmp_path) == before


def test_fixture_mode_refuses_a_pre_existing_target_with_no_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixtures = _fixture_mode_sandbox(tmp_path, monkeypatch)
    target = fixtures / "target"
    target.mkdir()
    (target / "keep.txt").write_bytes(b"not yours to delete\n")

    before = _tree_digest(fixtures)
    assert d5.main(["source", "target", "--formals", "gain"]) == 1
    assert _tree_digest(fixtures) == before


def test_fixture_mode_builds_a_new_target_inside_the_fixture_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixtures = _fixture_mode_sandbox(tmp_path, monkeypatch)

    assert d5.main(["source", "target", "--formals", "gain"]) == 0
    assert _tree_digest(fixtures / "target") == _tree_digest(fixtures / "source")


def test_build_variant_tree_refuses_overlapping_source_and_target(
    tmp_path: Path,
) -> None:
    """The mechanism-level invariant: the target is deleted before the copy, so
    an aliased or nested pair must raise instead of destroying the source."""
    source = tmp_path / "source"
    (source / "sub").mkdir(parents=True)
    (source / "model.sysml").write_text("package p {}\n")

    for target in (source, source / "sub", tmp_path):
        with pytest.raises(ValueError, match="overlaps"):
            d5.build_variant_tree(source, target, ["gain"])
    assert (source / "model.sysml").read_text() == "package p {}\n"


def test_precondition_c_keeps_same_named_definitions_distinct(tmp_path: Path) -> None:
    """Audit F3: two packages each declare `calc def Revenue`; only one declares
    the formal being renamed. A lookup that collapses them to one simple-name key
    could let either definition stand in for the other, so the precondition must
    refuse when any same-named candidate lacks the formal."""
    root = _hazard_tree(
        tmp_path,
        """package LibA {
    private import ScalarValues::*;

    calc def Revenue {
        in attribute gain : Real;
        out attribute revenue : Real = gain * 2.0;
    }
}
package LibB {
    private import ScalarValues::*;

    calc def Revenue {
        in attribute other : Real;
        out attribute revenue : Real = other * 3.0;
    }
}
package Design {
    private import LibA::*;

    part def Plant {
        attribute gain : Real = 1.0;
        calc revenue_calc : Revenue { in gain = gain; }
    }

    part plant : Plant;
}
""",
    )
    _refuses_without_writing(root, ["gain"], "(c)", tmp_path)
