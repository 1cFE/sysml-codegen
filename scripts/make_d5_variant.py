#!/usr/bin/env python3
"""Author a D-5 migrated variant of a fixture the exact route refuses, and prove it.

The exact route refuses a binding whose right-hand side resolves to its own formal
(``SI_SELF_BINDING``): the binding is legal, inert SysML that supplies no enclosing feature.
The ratified migration for a real model is renaming — the fifteen-rename D-5 migration Slice
3D ran on the customer model — and this applies the same recipe mechanically.

**The originals are never touched.** A variant is a new fixture beside the original, so a
fixture written to pin the refused shape keeps pinning it, and the ratified corpus rows keep
their subjects. Variants join no corpus ledger.

The recipe, applied per refused formal:

- inside the ``calc def`` or ``constraint def`` that declares it, the formal and every use of
  it in that block gain an ``_in`` suffix;
- at every ``calc``/``assert constraint`` usage binding, the *left* side gains the suffix and
  the right side does not — which is precisely what stops the binding resolving to itself.

**The proof is a strip check, not a diff review.** Removing the ``_in`` suffix from the
renamed names everywhere in the variant must reproduce the original **byte for byte**. That
holds only if the rename is the sole edit, so it catches a stray reformat, a dropped comment
or a hand-tweaked value that a reviewer reading a large diff would miss. It is checkable
without a license.

Usage::

    python scripts/make_d5_variant.py catf_mfe_model catf_mfe_d5
    python scripts/make_d5_variant.py --check catf_mfe_model catf_mfe_d5
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
BATCH_MANIFEST = FIXTURES / "v6_recapture_batch/batch.json"

#: Files a variant does not inherit: a snapshot belongs to the fixture it was captured from,
#: and a variant's own graph differs from its original's by construction.
NOT_INHERITED = {"instance_graph_snapshot.json"}

#: The v5 extraction snapshot's filename. Corpus membership used to be exactly this file's
#: presence — it is what the corpus was enumerated by, and what the 37 rows named. The file
#: retired with the v5 family (retirement step 2), so the name is kept only as the tripwire
#: ``test_d5_variants.py`` uses to say it has not come back. A variant may carry its own *v6*
#: snapshot — that is what lets a repointed test read it without a licence.
RETIRED_CORPUS_MARKER = "extraction_snapshot.json"

#: Files a variant carries that its original does not, and which the strip check therefore
#: ignores because neither is part of the model: the provenance record that says why the
#: variant exists, and the variant's own sealed v6 graph, which exists precisely because the
#: original has none — the exact route refuses it.
VARIANT_ONLY = {"PROVENANCE.md", "instance_graph_snapshot.json"}


def refused_formals(fixture: str) -> list[str]:
    """The formal names the exact route refused for this fixture, from the batch record."""
    record = json.loads(BATCH_MANIFEST.read_text())["records"][fixture]
    if record["status"] != "refused":
        raise SystemExit(f"{fixture} is not refused; it needs no variant")
    unsupported = sorted(set(record["codes"]) - {"SI_SELF_BINDING"})
    if unsupported:
        raise SystemExit(
            f"STOP: {fixture} carries refusal codes the D-5 rename recipe does not "
            f"address: {unsupported}. That is a new premise finding, not a variant."
        )
    return sorted({line.rsplit(".", 1)[-1].strip() for line in record["message"].split("; ")})


#: The definition forms that declare ``in`` formals a usage then binds. Both are in the D-5
#: recipe's scope for the same reason: the refusal is about a binding whose right side
#: resolves to its own formal, and a ``constraint def`` declares formals exactly as a
#: ``calc def`` does. Renaming only the binding's left side without renaming the declaration
#: leaves the model inconsistent, which is what `gate_a_d5` measured on the first attempt
#: (generation refused with ``cross_scope_binding_disagreement``). Constraint-def names may be
#: single-quoted (``constraint def 'Viability Threshold'``).
_DEFINITION_BLOCK = re.compile(r"\b(?:calc|constraint)\s+def\s+('[^']+'|\w+)\s*\{")


def _definition_blocks(text: str) -> dict[str, tuple[int, int]]:
    """Span of every ``calc def`` / ``constraint def`` block, by brace depth."""
    blocks = {}
    for match in _DEFINITION_BLOCK.finditer(text):
        depth, index = 0, match.end() - 1
        while index < len(text):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    break
            index += 1
        blocks[match.group(1)] = (match.start(), index + 1)
    return blocks


def _rename_in_span(text: str, span: tuple[int, int], name: str) -> str:
    start, end = span
    body = re.sub(rf"\b{re.escape(name)}\b", f"{name}_in", text[start:end])
    return text[:start] + body + text[end:]


def _rename_binding_left_sides(text: str, name: str) -> str:
    """``in <name> = <expr>;`` becomes ``in <name>_in = <expr>;`` — left side only."""
    return re.sub(
        rf"(\bin\s+){re.escape(name)}(\s*=)", rf"\1{name}_in\2", text
    )




# --- Stage 2: the aggregation split ------------------------------------------
#
# The rename alone is not enough for an assembly that rolls several children up into one
# metric. The exact route names an expression parameter after the last member of a reference
# and drops the qualifier, so `sum(pv_module.raw_material_cost) + sum(inverter.raw_material_cost)`
# renders both terms `raw_material_cost` and projection refuses with SI_RENDERING_COLLISION.
# That refusal is ratified correct (S4); the cure is the `costed_cart_d5` shape — each term
# gets its own named attribute and the rollup adds those names.
#
# This is a *shape* change, so the strip check cannot cover it: no suffix removal recovers an
# original from a model with different attributes. What replaces byte-identity is an
# enumerated difference. Every added attribute is derived by one deterministic rule from the
# original, the whole list is written into the variant's README, and `strip_check` undoes
# exactly that list before comparing — so anything the list does not name survives the undo
# and fails the comparison. Nothing unlisted can ride along.

#: A rollup line and the terms it adds, as authored.
ROLLUP = re.compile(r"^(?P<indent>[ \t]*):>> (?P<metric>\w+) =\s*\n(?P<body>.*?;)\s*$", re.M | re.S)


def _terms(body: str) -> list[str]:
    return [term.strip() for term in body.rstrip(";").replace("\n", " ").split("+")]


def _rendered(term: str) -> str:
    """What the exact route will call this term's parameter: last member, qualifier dropped."""
    inner = re.sub(r"^sum\((.*)\)$", r"\1", term).strip()
    return inner.rsplit(".", 1)[-1]


def _intermediate_name(term: str) -> str:
    """A deterministic name for one term's contribution: its reference path, flattened."""
    inner = re.sub(r"^sum\((.*)\)$", r"\1", term).strip()
    return inner.replace(".", "_")


def aggregation_rewrites(text: str) -> list[dict]:
    """Every rollup whose terms collide, and the named intermediates that separate them.

    Derived from the text by one rule, never hand-listed, so the enumeration in the README is
    reproducible rather than maintained.
    """
    rewrites = []
    for match in ROLLUP.finditer(text):
        terms = _terms(match.group("body"))
        if len(terms) < 2:
            continue
        rendered = [_rendered(term) for term in terms]
        if len(set(rendered)) == len(rendered):
            continue
        indent = match.group("indent")
        added, replacements = [], []
        for term in terms:
            if "." not in term:
                replacements.append(term)
                continue
            name = _intermediate_name(term)
            added.append(f"{indent}attribute {name} : Real = {term};")
            replacements.append(name)
        rollup = f"{indent}:>> {match.group('metric')} =\n"
        rollup += " +\n".join(f"{indent}    {name}" for name in replacements) + ";"
        rewrites.append(
            {
                "metric": match.group("metric"),
                "terms": terms,
                "added": added,
                "original": match.group(0).rstrip(),
                "rewritten": "\n".join(added) + "\n" + rollup,
            }
        )
    return rewrites


def apply_aggregation_split(text: str) -> str:
    for rewrite in aggregation_rewrites(text):
        text = text.replace(rewrite["original"], rewrite["rewritten"], 1)
    return text


def undo_aggregation_split(text: str, rewrites: list[dict]) -> str:
    for rewrite in rewrites:
        text = text.replace(rewrite["rewritten"], rewrite["original"], 1)
    return text


def build_variant(source: str, target: str, formals: list[str]) -> list[Path]:
    source_dir, target_dir = FIXTURES / source, FIXTURES / target
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(
        source_dir,
        target_dir,
        ignore=lambda _directory, names: {n for n in names if n in NOT_INHERITED},
    )

    written = []
    for file in sorted(target_dir.rglob("*.sysml")):
        text = original = file.read_text()
        for name in formals:
            # Late blocks first: renaming shifts offsets, so earlier spans stay valid.
            for span in sorted(
                (span for span in _definition_blocks(text).values()), reverse=True
            ):
                declares = rf"\bin\s+attribute\s+{re.escape(name)}\b"
                if re.search(declares, text[span[0] : span[1]]):
                    text = _rename_in_span(text, span, name)
            text = _rename_binding_left_sides(text, name)
        text = apply_aggregation_split(text)
        if text != original:
            file.write_text(text)
            written.append(file.relative_to(ROOT))
    return written


def strip_check(source: str, target: str, formals: list[str]) -> list[str]:
    """Removing the suffix must reproduce the original byte for byte, file for file."""
    source_dir, target_dir = FIXTURES / source, FIXTURES / target
    problems = []

    # VARIANT_ONLY is excluded from BOTH sides. A provenance record belongs to the fixture it
    # sits in, so a source that carries one of its own (the occurrence-demand fixtures each
    # do) must not make the variant's own record read as a missing file.
    originals = {
        path.relative_to(source_dir)
        for path in source_dir.rglob("*")
        if path.is_file() and path.name not in NOT_INHERITED | VARIANT_ONLY
    }
    variants = {
        path.relative_to(target_dir)
        for path in target_dir.rglob("*")
        if path.is_file() and path.name not in VARIANT_ONLY
    }
    for missing in sorted(originals - variants):
        problems.append(f"variant is missing {missing}")
    for extra in sorted(variants - originals):
        problems.append(f"variant carries {extra}, which the original does not")

    for relative in sorted(originals & variants):
        stripped = (target_dir / relative).read_text()
        # Undo the enumerated aggregation edits first, then the renames. An edit the
        # enumeration does not name survives this and fails the byte comparison below.
        renamed = (source_dir / relative).read_text()
        for name in formals:
            for span in sorted(_definition_blocks(renamed).values(), reverse=True):
                if re.search(rf"\bin\s+attribute\s+{re.escape(name)}\b", renamed[span[0]:span[1]]):
                    renamed = _rename_in_span(renamed, span, name)
            renamed = _rename_binding_left_sides(renamed, name)
        stripped = undo_aggregation_split(stripped, aggregation_rewrites(renamed))
        for name in formals:
            stripped = re.sub(rf"\b{re.escape(name)}_in\b", name, stripped)
        if stripped.encode() != (source_dir / relative).read_bytes():
            problems.append(f"stripping {relative} does not reproduce the original bytes")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument("--check", action="store_true", help="strip-check only; write nothing")
    parser.add_argument(
        "--formals",
        help=(
            "comma-separated refused formals, for a fixture with no batch record. The batch "
            "manifest only covers the 37 corpus fixtures; a non-corpus fixture's formals come "
            "from the exact route's own refusal message, which is what the manifest records. "
            "Supplying them here is a caller decision, so the caller states where they came "
            "from — the manifest stays the only automatic source."
        ),
    )
    args = parser.parse_args(argv)

    formals = (
        sorted({name.strip() for name in args.formals.split(",")})
        if args.formals
        else refused_formals(args.source)
    )
    if not args.check:
        written = build_variant(args.source, args.target, formals)
        print(f"{args.target}: {len(formals)} formals renamed across {len(written)} files")
        for path in written:
            print(f"   {path}")

    problems = strip_check(args.source, args.target, formals)
    for problem in problems:
        print(f"FAIL {problem}")
    print(f"strip check: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
