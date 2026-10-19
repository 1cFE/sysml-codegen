import json, sys, collections, re
b = json.load(open(sys.argv[1]))["roots"]; h = json.load(open(sys.argv[2]))["roots"]
assert b.keys() == h.keys()
cat = collections.Counter(k.split(":")[0] for k in b)
print("roots", len(b), dict(cat))
for side, d in (("base", b), ("head", h)):
    c = collections.Counter((k.split(":")[0], str(v["result"])) for k, v in d.items())
    print(side, sorted(c.items()))
    print(side, "totals", collections.Counter(str(v["result"]) for v in d.values()))
print("--- outcome diffs")
for k in b:
    if b[k]["result"] != h[k]["result"]: print(k, b[k]["result"], h[k]["result"])
print("--- byte diffs")
for k in b:
    if b[k].get("sha") != h[k].get("sha"): print(k, b[k].get("sha"), h[k].get("sha"))
print("--- exc text diffs")
for k in b:
    if b[k].get("exc") != h[k].get("exc"): print(k, "\n  B:", b[k].get("exc"), "\n  H:", h[k].get("exc"))
print("--- log diffs")
for k in b:
    lb, lh = b[k]["logs"], h[k]["logs"]
    if lb != lh:
        sb = collections.Counter(map(tuple, lb)); sh = collections.Counter(map(tuple, lh))
        print("##", k, b[k]["result"])
        for r in (sb - sh).elements(): print("  -", r)
        for r in (sh - sb).elements(): print("  +", r)
