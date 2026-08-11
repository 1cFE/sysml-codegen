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

- inside the ``calc def`` that declares it, the formal and every use of it in that block
  gain an ``_in`` suffix;
- at every ``calc <usage> : <ThatCalcDef>`` binding, the *left* side gains the suffix and the
  right side does not — which is precisely what stops the binding resolving to itself.

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

#: Files a variant does not inherit. The v5 snapshot belongs to the corpus fixture it was
#: captured from; a variant is not a corpus fixture and must never look like one.
NOT_INHERITED = {"extraction_snapshot.json", "instance_graph_snapshot.json"}

#: Files a variant carries that its original does not, and which the strip check therefore
#: ignores. Only provenance: a variant must explain why it exists, and the explanation is not
#: part of the model.
VARIANT_ONLY = {"PROVENANCE.md"}


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


def _calc_def_blocks(text: str) -> dict[str, tuple[int, int]]:
    """Span of every ``calc def <Name> { ... }`` block, by brace depth."""
    blocks = {}
    for match in re.finditer(r"\bcalc\s+def\s+(\w+)\s*\{", text):
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
                (span for span in _calc_def_blocks(text).values()), reverse=True
            ):
                declares = rf"\bin\s+attribute\s+{re.escape(name)}\b"
                if re.search(declares, text[span[0] : span[1]]):
                    text = _rename_in_span(text, span, name)
            text = _rename_binding_left_sides(text, name)
        if text != original:
            file.write_text(text)
            written.append(file.relative_to(ROOT))
    return written


def strip_check(source: str, target: str, formals: list[str]) -> list[str]:
    """Removing the suffix must reproduce the original byte for byte, file for file."""
    source_dir, target_dir = FIXTURES / source, FIXTURES / target
    problems = []

    originals = {
        path.relative_to(source_dir)
        for path in source_dir.rglob("*")
        if path.is_file() and path.name not in NOT_INHERITED
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
    args = parser.parse_args(argv)

    formals = refused_formals(args.source)
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
