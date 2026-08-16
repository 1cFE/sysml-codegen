"""Report the exact deep-literal-redefinition fact shape for each candidate model.

The lane under test is ``_apply_deep_literal_redefinitions``
(``src/sysml_codegen/elaboration/elaborate.py:1032``): an anonymous feature carrying a
feature-value expression whose owned redefinition targets a *chained* feature. This
probe walks that exact trigger, rebuilds the same reference fact the elaborator would
build, and reports typed identities — exact element IDs, never name strings.

A D11 affected shape needs a fact with exactly one segment whose leaf's live semantic
owner is a ``PartUsage``. That is the only input that reaches the one-segment branch at
``elaborate.py:2062-2076``; the lane's own ``plural=True`` call never applies to it,
because the one-segment branch returns before ``plural`` is consulted (design D4).

Sections:

1. ``candidates`` — the authored candidate models kept beside this file.
2. ``census`` — every tracked fixture root whose text contains a chained redefinition,
   loaded and walked through the same lane trigger. This bounds the search surface; it
   cannot prove the shape impossible.

Run from the repository root with the SysIDE license loaded:

    set -a; source ../agentic-mbse/.env; set +a
    uv run python .project/active/qualified-reference-occurrence-anchoring/\
spike/deep-override-authorability/probe.py
"""

import re
import sys
from pathlib import Path

from agentic_mbse.sysml.expression import resolved_target_fact
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration.elaborate import elaborate
from sysml_codegen.extraction.extractor import SysMLDataExtractor

ROOT = Path(__file__).parent
REPO = ROOT.parents[4]
FIXTURES = REPO / "tests" / "fixtures"

# A redefinition whose target is a dotted feature chain — the only authored spelling
# observed to reach the deep-literal lane.
CHAINED_REDEFINITION = re.compile(r":>>\s*[\w']+(\s*\.\s*[\w']+)+")

CASES = sorted(path.name for path in ROOT.iterdir() if path.is_dir() and path.name[0] == "c")


def semantic_owner(element):
    """The owning type of a feature — the elaborator's owner question."""
    return getattr(element, "owning_type", None)


def describe(element):
    if element is None:
        return {"id": None, "metatype": None, "name": None, "qn": None}
    return {
        "id": str(SysideAdapter.element_id(element)),
        "metatype": type(element).__name__,
        "name": str(getattr(element, "name", None)),
        "qn": str(getattr(element, "qualified_name", None)),
    }


def deep_literal_sites(model):
    """Every element that reaches the deep-literal-override lane, with its chain."""
    sites = []
    for feature in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True):
        if getattr(feature, "qualified_name", None) is not None:
            continue
        expression = getattr(feature, "feature_value_expression", None)
        if expression is None:
            continue
        for relationship in getattr(feature, "owned_redefinitions", ()) or ():
            redefined = getattr(relationship, "redefined_feature", None)
            chain = list(getattr(redefined, "chaining_features", ()) or [])
            if not chain:
                continue
            sites.append(
                {
                    "writer": feature,
                    "redefined": redefined,
                    "chain": chain,
                    "facts": [
                        fact
                        for link in chain
                        if (fact := resolved_target_fact(link)) is not None
                    ],
                }
            )
    return sites


def verdict(site):
    """Label one site against the D11 affected shape."""
    facts = site["facts"]
    if len(facts) != 1:
        return f"NOT AFFECTED — {len(facts)} segments, one-segment branch not reached"
    leaf = next(
        link
        for link in site["chain"]
        if str(SysideAdapter.element_id(link)) == facts[-1].element_id
    )
    owner = semantic_owner(leaf)
    if not SysideAdapter.is_instance(owner, "PartUsage"):
        return f"NOT AFFECTED — one segment, but owner metatype is {type(owner).__name__}"
    return "AFFECTED SHAPE FOUND — one segment, PartUsage owner"


def walk(label, root, *, run_elaborate):
    extractor = SysMLDataExtractor([root])
    loaded = extractor.load_models()
    validation = list(getattr(extractor.diagnostics, "validation", ()) or ())
    print(f"=== {label} loaded={loaded} validation_diagnostics={len(validation)}")
    for diagnostic in validation[:6]:
        print(f"    diagnostic: {diagnostic}")
    if not loaded:
        return
    sites = deep_literal_sites(extractor.model)
    print(f"    deep-literal lane sites: {len(sites)}")
    for index, site in enumerate(sites):
        print(f"    site[{index}] writer={describe(site['writer'])}")
        print(f"      writer_owner={describe(semantic_owner(site['writer']))}")
        print(f"      redefined={describe(site['redefined'])}")
        for link_index, link in enumerate(site["chain"]):
            print(f"      chain[{link_index}]={describe(link)}")
            print(f"        live_owner={describe(semantic_owner(link))}")
        for fact_index, fact in enumerate(site["facts"]):
            print(
                f"      fact[{fact_index}] element_id={fact.element_id} "
                f"owner_element_id={fact.owner_element_id} "
                f"owner_is_definition={fact.owner_is_definition}"
            )
        print(f"      VERDICT: {verdict(site)}")
    if not run_elaborate:
        return
    # Exercise the real lane end to end, including its plural=True resolver call.
    try:
        graph = elaborate(
            extractor.model,
            extractor.extract_calculation_definitions(),
            validation_diagnostics=extractor.diagnostics.validation,
            strict=False,
        )
    except Exception as error:  # noqa: BLE001 — a probe reports, it does not fail the run
        print(f"    elaborate raised {type(error).__name__}: {error}")
        return
    print(f"    elaborate diagnostics={[d.code.value for d in graph.diagnostics]}")
    for node in graph.attrs.values():
        print(
            f"    attr declaration={node.node_id.declaration.root_declaration.value} "
            f"value={node.value} value_site={node.value_site.value}"
        )


def census_roots():
    """Tracked fixture roots whose text contains a chained redefinition."""
    roots = set()
    for path in FIXTURES.rglob("*.sysml"):
        if CHAINED_REDEFINITION.search(path.read_text()):
            roots.add(path.relative_to(FIXTURES).parts[0])
    return sorted(roots)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "candidates"):
        print("## candidates")
        for case in CASES:
            walk(case, ROOT / case, run_elaborate=True)
    if mode in ("all", "census"):
        print("## census")
        roots = census_roots()
        print(f"census roots with a chained redefinition: {len(roots)}")
        for name in roots:
            walk(f"fixture:{name}", FIXTURES / name, run_elaborate=False)


main()
