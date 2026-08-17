#!/usr/bin/env python3
"""Diff two ``corpus_compare.py`` ledgers and list every difference for adjudication.

This decides nothing. It reads two captured ledgers, keys their rows by typed identity,
and prints the exact set of differences a human must rule on in ``adjudication.md``:
changed site keys, changed outcomes, changed refusals, and any change to the per-root
identity block (occurrence wire IDs and slot-derived node IDs).

It refuses rather than reports when a root that elaborated carries no identity block.
An absence is not agreement, and a comparison it never made is not a comparison it
passed.

Usage::

    uv run python .project/completed/20260816_qualified-reference-occurrence-anchoring/\
verification/adjudicate.py before.json after.json

No license is needed: both inputs are already-captured JSON.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SECTIONS = ("corpus", "promoted")


def site_key(site: dict[str, Any]) -> tuple[str, ...]:
    return (
        site["root"],
        site["lane"],
        site["consumer"],
        str(site["reference_ordinal"]),
        site["leaf_declaration"],
    )


def sites_by_key(ledger: dict[str, Any], section: str) -> dict[tuple[str, ...], dict[str, Any]]:
    return {
        site_key(site): site
        for root in ledger[section]
        for site in root.get("sites", ())
    }


def refusals(ledger: dict[str, Any], section: str) -> dict[str, str]:
    return {
        root["root"]: root["refused"]
        for root in ledger[section]
        if root.get("refused") is not None
    }


class MissingIdentityBlockError(Exception):
    """A ledger row that should carry an identity block does not."""


def identity(ledger: dict[str, Any], section: str, side: str) -> dict[str, Any]:
    """Per-root identity blocks, refusing a ledger that omits one.

    An absent block is not agreement. Mapping two absences to ``None`` and comparing
    them equal is how a 13-root identity proof was once reported as covering 153: the
    roots were counted as compared while nothing about them was measured. A root that
    elaborated therefore *must* carry a block, and this refuses the whole run when one
    does not, rather than returning a verdict over evidence it does not have.

    A refused root is the one legitimate absence: it produced no graph, so there are no
    occurrence records or node IDs to freeze. Its refusal string is compared instead,
    and a root that starts or stops refusing shows up there.
    """
    blocks: dict[str, Any] = {}
    for root in ledger[section]:
        if root.get("refused") is not None:
            continue
        block = root.get("identity")
        if block is None:
            raise MissingIdentityBlockError(
                f"{side} ledger: root {root['root']!r} in section {section!r} elaborated "
                "but carries no identity block, so its identities cannot be compared"
            )
        blocks[root["root"]] = block
    return blocks


def report(before: dict[str, Any], after: dict[str, Any]) -> int:
    problems = 0
    for section in SECTIONS:
        b, a = sites_by_key(before, section), sites_by_key(after, section)
        print(f"\n=== {section}: {len(b)} before sites, {len(a)} after sites ===")

        only_before, only_after = sorted(set(b) - set(a)), sorted(set(a) - set(b))
        print(f"site keys only in before: {len(only_before)}")
        for key in only_before:
            print("  -", key)
        print(f"site keys only in after: {len(only_after)}")
        for key in only_after:
            print("  +", key)
        problems += len(only_before) + len(only_after)

        covered = {"edge", "diagnostic", "no_edge"}
        uncovered = [key for key, site in a.items() if site["outcome"]["kind"] not in covered]
        print(f"after rows with no edge / diagnostic / structural reason: {len(uncovered)}")
        problems += len(uncovered)

        changed = [key for key in sorted(set(b) & set(a)) if b[key]["outcome"] != a[key]["outcome"]]
        print(f"changed outcomes: {len(changed)}")
        for key in changed:
            print(f"\n  CHANGED {key}")
            print(f"    written : {a[key]['written_text']}")
            print(f"    owner   : {a[key]['owner_declaration']} ({a[key]['owner_metatype']})")
            print(f"    plural  : {a[key]['plural_caller']}")
            print(f"    before  : {json.dumps(b[key]['outcome'], sort_keys=True)}")
            print(f"    after   : {json.dumps(a[key]['outcome'], sort_keys=True)}")

        rb, ra = refusals(before, section), refusals(after, section)
        refusal_diff = {
            root: (rb.get(root), ra.get(root))
            for root in sorted(set(rb) | set(ra))
            if rb.get(root) != ra.get(root)
        }
        print(f"\nchanged refusals: {len(refusal_diff)}")
        for root, pair in refusal_diff.items():
            print(f"  {root}: {pair[0]!r} -> {pair[1]!r}")
        problems += len(refusal_diff)

        ib, ia = identity(before, section, "before"), identity(after, section, "after")
        both = set(ib) & set(ia)
        identity_diff = [root for root in sorted(both) if ib[root] != ia[root]]
        one_sided = sorted(set(ib) ^ set(ia))
        print(
            f"roots with a changed identity block: {len(identity_diff)} of {len(both)} "
            f"compared ({len(set(rb) | set(ra))} refused on one side or both, so they "
            "have no identity to compare)"
        )
        for root in identity_diff:
            print("  !", root)
        for root in one_sided:
            print(f"  ! {root}: identity present on exactly one side")
        problems += len(identity_diff) + len(one_sided)

        # Catch-all: any field of a root record that the checks above do not cover
        # (graph diagnostics, deep-override lane counts, unsupported-expression consumers).
        rb_all = {root["root"]: root for root in before[section]}
        ra_all = {root["root"]: root for root in after[section]}
        other = {
            root: [
                field
                for field in sorted(set(rb_all[root]) | set(ra_all[root]))
                if field not in {"sites", "identity", "refused"}
                and rb_all[root].get(field) != ra_all[root].get(field)
            ]
            for root in sorted(set(rb_all) & set(ra_all))
        }
        other = {root: fields for root, fields in other.items() if fields}
        # A root-level diagnostic list moving in step with one of its own changed sites is
        # the same event seen twice, so it is reported but not counted as drift. A change
        # on a root with no changed site would be, and is flagged.
        changed_roots = {key[0] for key in changed}
        print(f"roots with any other changed field: {len(other)}")
        for root, fields in other.items():
            paired = "paired with a changed site" if root in changed_roots else "UNPAIRED"
            print(f"  ? {root}: {fields} [{paired}]")
            for field in fields:
                print(f"      before: {json.dumps(rb_all[root].get(field), sort_keys=True)[:400]}")
                print(f"      after : {json.dumps(ra_all[root].get(field), sort_keys=True)[:400]}")
        problems += sum(1 for root in other if root not in changed_roots)

    print(f"\ntotals before: {json.dumps(before['totals'], sort_keys=True)}")
    print(f"totals after : {json.dumps(after['totals'], sort_keys=True)}")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    before = json.loads(args.before.read_text())
    after = json.loads(args.after.read_text())
    problems = report(before, after)
    print(
        "\nstructural problems (missing keys, uncovered rows, refusal or identity drift): "
        f"{problems}"
    )


if __name__ == "__main__":
    main()
