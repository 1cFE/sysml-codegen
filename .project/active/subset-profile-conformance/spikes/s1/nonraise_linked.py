"""Spike S1: list the rule- or row-linked public sites whose statement is not a raise, with the statement."""
import csv, sys, ast
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import elide as e
ACCOUNT = "/home/reid/src/subset-conformance/agentic-mbse/tests/fixtures/subset_profile/inventory/site_account.csv"
rows = [r for r in csv.DictReader(l for l in open(ACCOUNT) if not l.startswith("#"))
        if r["role"] == "public_capability" and (r["rule"] or r["matrix_row"])]
for r in rows:
    try:
        e.elide(r["site_id"]).restore(); continue
    except e.ElisionError as err:
        stmt = str(err).split("not Raise: ")[1][:90]
    print(f"{r['site_id'].split('::',1)[0].rsplit('/',1)[-1]}:{r['line']} {r['site_id'].split('::')[1]} [{r['rule'] or r['matrix_row']}]\n    {stmt}")
