#!/usr/bin/env python3
"""Corpus prevalence scan (SOURCE-IDENTITY Item 1): count binding authoring forms.

Textual scan (no parser, no license) over every ``in <param> = <rhs>;`` line in
the three model corpora. This is a prevalence estimate for the migration-cost
column of the authoring-form table — classification is syntactic and documented
below, and every non-obvious RHS keeps a file:line example so a reader can audit
the bucket.

Buckets (RHS classification, in priority order):
- literal        — number/string/boolean (with optional unit bracket "3.0 [m]")
- hash_indexed   — contains ``#(``  (KerML index operator)
- sq_bracketed   — contains ``[`` not part of a literal-with-unit
- qualified      — contains ``::``
- chain          — contains ``.`` outside a decimal number
- bare_selfnamed — single identifier, identical to the bound param name
- bare_renamed   — single identifier, different from the param name
- expression     — anything else (operators, calls, conditionals)

Typed declarations ``in x : T = v;`` (calc-def parameter defaults) are counted
separately from usage rebindings ``in x = v;`` — the authoring-form question is
about usage bindings.

Usage:
    python3 probes/scan_corpus.py            # no license needed
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SPIKE_DIR = Path(__file__).resolve().parent
RAW_DIR = SPIKE_DIR / "raw"

# Live authored trees only: .venv (vendored stdlib/syside library) and archive/
# would otherwise dominate the counts with non-project models.
CORPORA = {
    "sysml-codegen fixtures": Path("/home/reid/1cfe/sysml-codegen/tests/fixtures"),
    "fusion-tea models/": Path("/home/reid/1cfe/fusion-tea/models"),
    "stellarator-demo models/": Path(
        "/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/models"
    ),
}

# `in [attribute] <name> [: Type] = <rhs>;`  (single-line bindings only; the
# corpora author bindings one per line — spot-check any miss manually)
BINDING_RE = re.compile(
    r"^\s*in\s+(?:attribute\s+|ref\s+)?"
    r"(?P<param>'[^']+'|[A-Za-z_][\w]*)\s*"
    r"(?P<typed>:\s*[^=;]+)?"
    r"=\s*(?P<rhs>[^;]+);"
)

LITERAL_RE = re.compile(
    r"^(?:-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|\"[^\"]*\")"
    r"(?:\s*\[[^\]]+\])?$"  # optional unit bracket
)
BARE_RE = re.compile(r"^(?:'[^']+'|[A-Za-z_]\w*)$")
DECIMAL_DOT_RE = re.compile(r"\d\.\d")


def classify(param: str, rhs: str) -> str:
    rhs = rhs.strip()
    if LITERAL_RE.match(rhs):
        return "literal"
    if "#(" in rhs:
        return "hash_indexed"
    if "[" in rhs:
        return "sq_bracketed"
    if BARE_RE.match(rhs):
        return "bare_selfnamed" if rhs.strip("'") == param.strip("'") else "bare_renamed"
    if "::" in rhs:
        return "qualified"
    dotless = DECIMAL_DOT_RE.sub("00", rhs)
    if "." in dotless:
        # A pure two-plus-segment identifier chain vs a larger expression.
        if re.match(r"^(?:'[^']+'|[A-Za-z_]\w*)(?:\.(?:'[^']+'|[A-Za-z_]\w*))+$", rhs):
            return "chain"
        return "expression"
    return "expression"


def main() -> int:
    RAW_DIR.mkdir(exist_ok=True)
    report: dict[str, dict] = {}
    for corpus, root in CORPORA.items():
        counts: dict[str, int] = {}
        typed_defaults = 0
        examples: dict[str, list[str]] = {}
        for f in sorted(root.rglob("*.sysml")):
            try:
                lines = f.read_text(errors="replace").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                m = BINDING_RE.match(line)
                if not m:
                    continue
                if m.group("typed"):
                    typed_defaults += 1
                    continue
                bucket = classify(m.group("param"), m.group("rhs"))
                counts[bucket] = counts.get(bucket, 0) + 1
                ex = examples.setdefault(bucket, [])
                if len(ex) < 8:
                    ex.append(f"{f.relative_to(root)}:{i}: {line.strip()}")
        report[corpus] = {
            "root": str(root),
            "usage_binding_counts": dict(sorted(counts.items())),
            "typed_param_defaults_skipped": typed_defaults,
            "examples": examples,
        }

    out = RAW_DIR / "corpus_scan.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    for corpus, rec in report.items():
        total = sum(rec["usage_binding_counts"].values())
        print(f"\n== {corpus} ({total} usage bindings; "
              f"{rec['typed_param_defaults_skipped']} typed defaults skipped)")
        for bucket, n in rec["usage_binding_counts"].items():
            print(f"  {bucket:>15}: {n}")
    print(f"\n[raw retained: {out}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
