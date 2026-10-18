"""Spike S1: try the elision helper on every scanned site (apply, then restore at once; no
model runs). Tally by result, by statement kind, and by the account's role column."""
import csv, sys
from collections import Counter
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import elide as e
GEN = "--generalized" in sys.argv

ACCOUNT = "/home/reid/src/subset-conformance/agentic-mbse/tests/fixtures/subset_profile/inventory/site_account.csv"
role = {r["site_id"]: (r["role"], r["disposition"], r["rule"], r["matrix_row"])
        for r in csv.DictReader(l for l in open(ACCOUNT) if not l.startswith("#"))}
tally, by_role, failures = Counter(), Counter(), []
for sid in sorted(e.site_rows()):
    try:
        el = e.elide(sid, generalized=GEN); el.restore(); res = "elided"
    except e.ElisionError as err:
        msg = str(err)
        res = "not-raise:" + msg.split("site statement is ")[1].split(",")[0] if "not Raise" in msg else "error"
        if res == "error": failures.append((sid, msg))
    except Exception as err:  # noqa: BLE001
        res = f"crash:{type(err).__name__}"; failures.append((sid, repr(err)))
    tally[res] += 1
    r, disp, rule, row = role.get(sid, ("?", "?", "", ""))
    linked = "rule-or-row" if (rule or row) else "unlinked"
    by_role[(r, linked, res)] += 1
print("by result:", dict(tally))
print("\nby (role, linked to a rule or matrix row, result):")
for k, v in sorted(by_role.items()): print(f"  {v:4d}  {k}")
print("\nfailures:")
for f in failures: print(" ", f)
