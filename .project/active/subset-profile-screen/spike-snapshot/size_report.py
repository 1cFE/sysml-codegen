"""Throwaway: how much would sealing the facts grow each committed snapshot?

Usage: python3 size_report.py OUT_DIR   (OUT_DIR from `probe_roundtrip.py ... --dump-facts`)

For each of the 23 committed snapshots, reports the envelope's current size, the spike codec's
size (type-tagged, an upper bound), and a "plain" size: the same tree with every type tag
dropped (dataclass -> object of fields, enum -> value, UUID -> string, tuple/frozenset -> list),
which is close to what a named-field schema would cost. Also the plain size of each top-level
SubsetFacts field, to show what dominates. No license needed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def plain(x):
    if isinstance(x, list):
        return [plain(i) for i in x]
    if not isinstance(x, dict):
        return x
    if "$e" in x:
        return x["v"]
    if "$f" in x:
        return float.fromhex(x["$f"]) if not x["$f"].endswith(("inf", "nan")) else x["$f"]
    if "$u" in x:
        return x["$u"]
    if "$t" in x:
        return [plain(i) for i in x["$t"]]
    if "$fs" in x:
        return [plain(i) for i in x["$fs"]]
    if "$m" in x:
        return [[plain(k), plain(v)] for k, v in x["$m"]]
    if "$d" in x:
        return {k: plain(v) for k, v in x["f"].items()}
    raise ValueError(x)


def size(obj) -> int:
    return len(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())


def main() -> None:
    out = Path(sys.argv[1])
    sources = json.loads((HERE / "sources.json").read_text())
    print(
        "| snapshot | envelope bytes | facts, tagged | facts, plain | growth (plain) "
        "| largest fields (plain bytes) |"
    )
    print("|---|---:|---:|---:|---:|---|")
    tot_env = tot_plain = 0
    for snap in sources:
        name = Path(snap).parent.name
        env = (REPO / snap).stat().st_size
        tagged_text = (out / f"snapshot__{name}.facts.json").read_text()
        tree = plain(json.loads(tagged_text))
        p = size(tree)
        fields = sorted(((size(v), k) for k, v in tree.items()), reverse=True)[:3]
        tot_env += env
        tot_plain += p
        print(
            f"| {name} | {env:,} | {len(tagged_text.encode()):,} | {p:,} | {p / env:+.0%} | "
            + ", ".join(f"{k} {n:,}" for n, k in fields)
            + " |"
        )
    print(f"| **total** | {tot_env:,} | | {tot_plain:,} | {tot_plain / tot_env:+.0%} | |")


if __name__ == "__main__":
    main()
