"""The published calculation-binding guidance cannot drift from what this route does.

The authoritative copy of the situational rule lives in agentic-mbse at
``docs/patterns/plant-idiom.md`` (self-binding-replacement D1). This contract makes the
published teaching falsifiable instead of trusted (D3):

* every fenced example carrying a ``@pinned`` provenance marker is compared with the
  sysml-codegen fixture it cites — content drift on either side fails here;
* exactly one document across all four instruction trees carries the authoritative
  marker, and the summary surfaces point at it;
* the self-named worked-example sweep returns nothing unmarked across ``claude/``,
  ``.claude/``, ``docs/patterns/`` and ``project_templates/`` — a refused shape may
  appear only inside an explicitly marked block or as prose (no trailing ``;``);
* the reviewed owner-qualified inventory is pinned file by file, with the two template
  sites recorded as rewritten to D-5 (owner ruling D11) and the three deliberate
  negatives still present.

The agentic tree comes from the explicit artifact-source manifest. The manifest
hashes the source archive and pairs it with the exact codegen extraction, so this
test never consults an editable sibling checkout. A separate agentic-mbse test
proves a built wheel carries the authoritative document byte for byte. License-free:
text only.

Marker grammar (parsed here, authored in the doc)::

    <!-- @pinned fixture=<codegen-rel-path> owner-class=<usage|definition|n/a> outcome=... -->
    <!-- @measured evidence="<free text>" owner-class=<...> outcome=<...> -->
    <!-- @authoritative calculation-binding-rule -->

A marker is immediately followed by one fenced ``sysml`` block. ``@pinned`` blocks are
checked by whitespace-normalized, order-preserving line containment in the cited file,
so doc examples may be dedented but not reworded.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.helpers.artifact_sources import agentic_source_root

CODEGEN_ROOT = Path(__file__).resolve().parents[2]

MARKED_EXAMPLE = re.compile(
    r"<!--\s*@(?P<kind>pinned|measured)\s+(?P<attrs>[^>]*?)-->\s*\n```sysml\n(?P<block>.*?)```",
    re.S,
)
AUTHORITATIVE = re.compile(r"<!--\s*@authoritative\s+calculation-binding-rule\s*-->")
ATTR = re.compile(r"(\w[\w-]*)=(\"[^\"]*\"|\S+)")
SELF_NAMED = re.compile(r"\bin\s+([\w']+)\s*=\s*\1\s*[;}]")
QUALIFIED_BINDING = re.compile(r"\bin\s+[\w']+\s*=\s*[^;=\n]*::")
ANY_BINDING = re.compile(r"\bin\s+[\w']+\s*=")

OWNER_CLASSES = {"usage", "definition", "n/a"}

#: The four instruction trees the sweep covers (relative to the agentic checkout root).
INSTRUCTION_TREES = ("claude", ".claude", "docs/patterns", "project_templates")

#: The reviewed owner-qualified inventory (design D11). Keys are files relative to the
#: agentic root; values are the expected positive-site counts after the review. The two
#: MODELING_PROCESS.md.template sites (pre-review lines 349-350) are absent because the
#: owner ruling rewrote them to the recommended D-5 form with the supported D-6 spelling
#: retained as a labelled prose alternative — that disposition is part of this record.
QUALIFIED_POSITIVE_SITES = {
    "docs/patterns/expose-pattern.md": 6,
    "docs/patterns/cross-file-binding.md": 2,
    "docs/patterns/adr002-calculations.md": 2,
    "docs/patterns/syntax-reference.md": 1,
    # All four are inside @pinned blocks of the authoritative document itself.
    "docs/patterns/plant-idiom.md": 4,
}

#: The three deliberate "Won't resolve!" negatives, retained as negatives.
QUALIFIED_NEGATIVE_FILES = (
    "docs/patterns/common-mistakes.md",
    "docs/patterns/cross-file-binding.md",
    "docs/patterns/syntax-reference.md",
)

#: Surfaces that carry the short rule plus a pointer to the authoritative copy (D2).
POINTER_SURFACES = (
    "claude/skills/sysml-conventions/SKILL.md",
    "project_templates/MODELING_PROCESS.md.template",
    "project_templates/MODELING_GUIDE.md.template",
)


def agentic_root() -> Path:
    """Return the explicit hash-identified agentic source tree."""
    root = agentic_source_root(CODEGEN_ROOT)
    missing = [tree for tree in INSTRUCTION_TREES if not (root / tree).is_dir()]
    assert not missing, f"agentic tree at {root} lacks {missing}"
    return root


def _text_files(root: Path, tree: str) -> list[Path]:
    files = []
    for path in sorted((root / tree).rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        files.append(path)
    return files


def _marked_examples(text: str) -> list[tuple[str, dict[str, str], str]]:
    examples = []
    for match in MARKED_EXAMPLE.finditer(text):
        attrs = {
            key: value.strip('"')
            for key, value in ATTR.findall(match.group("attrs"))
        }
        examples.append((match.group("kind"), attrs, match.group("block")))
    return examples


def _without_marked_blocks(text: str) -> str:
    return MARKED_EXAMPLE.sub("", text)


def _stripped_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _is_ordered_subsequence(needle: list[str], haystack: list[str]) -> bool:
    index = 0
    for line in needle:
        try:
            index = haystack.index(line, index) + 1
        except ValueError:
            return False
    return True


def _plant_idiom(root: Path) -> str:
    return (root / "docs" / "patterns" / "plant-idiom.md").read_text()


def test_exactly_one_authoritative_copy_across_all_instruction_trees() -> None:
    root = agentic_root()
    carriers = [
        path.relative_to(root)
        for tree in INSTRUCTION_TREES
        for path in _text_files(root, tree)
        if AUTHORITATIVE.search(path.read_text())
    ]
    assert carriers == [Path("docs/patterns/plant-idiom.md")], carriers


def test_marked_examples_carry_valid_labels() -> None:
    examples = _marked_examples(_plant_idiom(agentic_root()))
    assert examples, "the authoritative document carries no marked examples"
    for kind, attrs, _block in examples:
        assert attrs.get("owner-class") in OWNER_CLASSES, (kind, attrs)
        assert attrs.get("outcome"), (kind, attrs)
        if kind == "pinned":
            assert attrs.get("fixture"), attrs
        else:
            assert attrs.get("evidence"), attrs


def test_pinned_examples_match_their_cited_fixture_sources() -> None:
    """Content drift in either direction fails: the doc quotes the fixture, and
    the fixture is what the exact route demonstrably elaborates or refuses."""
    examples = _marked_examples(_plant_idiom(agentic_root()))
    pinned = [(attrs, block) for kind, attrs, block in examples if kind == "pinned"]
    assert len(pinned) >= 7, f"expected the seven pinned shapes, found {len(pinned)}"
    for attrs, block in pinned:
        fixture = CODEGEN_ROOT / attrs["fixture"]
        assert fixture.is_file(), f"cited fixture missing: {attrs['fixture']}"
        assert _is_ordered_subsequence(
            _stripped_lines(block), _stripped_lines(fixture.read_text())
        ), f"doc example drifted from {attrs['fixture']}:\n{block}"


def test_one_pinned_example_pins_the_refusal() -> None:
    """The negative is pinned too: at least one @pinned block cites a fixture the
    route refuses with SI_SELF_BINDING, and its snippet carries the refused form."""
    examples = _marked_examples(_plant_idiom(agentic_root()))
    refused = [
        (attrs, block)
        for kind, attrs, block in examples
        if kind == "pinned" and attrs.get("outcome", "").startswith("refused:SI_SELF_BINDING")
    ]
    assert len(refused) == 1, [attrs for attrs, _ in refused]
    assert SELF_NAMED.search(refused[0][1])


def test_zero_unmarked_self_named_examples_across_all_trees() -> None:
    """Invariant 2: the refused shape appears only inside an explicitly marked
    block. Prose warnings stay legal by carrying no statement terminator."""
    root = agentic_root()
    offenders = []
    for tree in INSTRUCTION_TREES:
        for path in _text_files(root, tree):
            remainder = _without_marked_blocks(path.read_text())
            if SELF_NAMED.search(remainder):
                offenders.append(str(path.relative_to(root)))
    assert offenders == [], offenders


def test_qualified_inventory_matches_the_reviewed_dispositions() -> None:
    """Design D11: every owner-qualified positive is a reviewed site. All retained
    sites qualify by the enclosing part usage and intend that usage's own feature
    (exact usage-owner class); the two former template sites are rewritten to D-5."""
    root = agentic_root()
    observed: dict[str, int] = {}
    for tree in INSTRUCTION_TREES:
        for path in _text_files(root, tree):
            positives = [
                line
                for line in path.read_text().splitlines()
                if QUALIFIED_BINDING.search(line) and "Won't resolve" not in line
            ]
            if positives:
                observed[str(path.relative_to(root))] = len(positives)
    assert observed == QUALIFIED_POSITIVE_SITES, observed

    # The authoritative document's own qualified examples are all pinned blocks.
    marked = "".join(block for _, _, block in _marked_examples(_plant_idiom(root)))
    assert len([line for line in marked.splitlines() if QUALIFIED_BINDING.search(line)]) == 4


def test_the_three_deliberate_negatives_remain() -> None:
    root = agentic_root()
    for relative in QUALIFIED_NEGATIVE_FILES:
        lines = [
            line
            for line in (root / relative).read_text().splitlines()
            if QUALIFIED_BINDING.search(line) and "Won't resolve" in line
        ]
        assert len(lines) == 1, f"{relative}: {lines}"


def test_summary_surfaces_point_at_the_authoritative_copy() -> None:
    """D2: the skill and both project templates carry the short rule and the
    pointer — never a second full copy (no @authoritative marker on them)."""
    root = agentic_root()
    for relative in POINTER_SURFACES:
        text = (root / relative).read_text()
        assert "plant-idiom.md" in text, relative
        assert "Binding a modelled value into a calculation" in text, relative
        assert not AUTHORITATIVE.search(text), f"{relative} claims authority"


def test_dot_claude_tree_still_has_no_binding_instruction_surface() -> None:
    """The plan-time inventory found no calculation-binding instruction under the
    tracked .claude tree, so no duplicate pointer was created there. This records
    that zero-edit result: a future binding surface in .claude becomes visible
    here and must either point at the authoritative copy or move to claude/."""
    root = agentic_root()
    offenders = [
        str(path.relative_to(root))
        for path in _text_files(root, ".claude")
        if ANY_BINDING.search(path.read_text())
    ]
    assert offenders == [], offenders
