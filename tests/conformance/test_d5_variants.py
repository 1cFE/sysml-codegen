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
    """A variant is not a corpus fixture. The v5 snapshot is what corpus membership means.

    Its own v6 snapshot is fine and in fact wanted: that is what lets a repointed test read
    the variant's graph without a licence. It joins no ledger either way.
    """
    assert not (d5.FIXTURES / variant / d5.CORPUS_MARKER).exists()


@pytest.mark.parametrize(("original", "variant"), VARIANTS)
def test_the_original_is_untouched_by_its_variant(original: str, variant: str) -> None:
    """The corpus guarantee: the refused original still carries the refused shape."""
    text = "".join(
        path.read_text() for path in sorted((d5.FIXTURES / original).rglob("*.sysml"))
    )
    for formal in d5.refused_formals(original):
        assert f"{formal}_in" not in text, f"{original} was edited in place"
    assert (d5.FIXTURES / original / "extraction_snapshot.json").is_file()


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
# The rename alone leaves an assembly's rollup refusing with SI_RENDERING_COLLISION, which is
# ratified correct behaviour. The cure is the costed_cart_d5 shape: one named attribute per
# term. A shape change cannot be proved by stripping a suffix, so these pin the three things
# that make the enumerated difference trustworthy — the summands did not change, the numbers
# are hand-derived, and the disease still fires without the cure.

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


def test_the_rename_alone_still_collides_so_the_cure_is_not_hiding_the_disease(
    tmp_path: Path,
) -> None:
    """Curing a refusal must not hide it. Without stage 2, the collision still fires."""
    from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline

    with pytest.raises(Exception) as refusal:
        build_elaborated_pipeline([_stage_one_only(tmp_path)])
    assert "SI_RENDERING_COLLISION" in str(refusal.value)


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
