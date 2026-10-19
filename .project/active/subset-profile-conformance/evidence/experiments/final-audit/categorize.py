import json, sys, collections, re
b = json.load(open(sys.argv[1]))["roots"]; h = json.load(open(sys.argv[2]))["roots"]
SUF = re.compile(r" \(reason: ([a-z0-9_]+)\)")
cats = collections.defaultdict(list); reasons = collections.Counter(); stub_reasons = collections.Counter()
stub_on = collections.Counter()
for k in b:
    sb = collections.Counter(map(tuple, b[k]["logs"])); sh = collections.Counter(map(tuple, h[k]["logs"]))
    rem = list((sb - sh).elements()); add = list((sh - sb).elements())
    for a in list(add):
        if "is a manual stub" in a[2]:
            add.remove(a); cats["stub"].append((k, a)); stub_on[str(b[k]["result"])] += 1
            stub_reasons[SUF.search(a[2]).group(1) if SUF.search(a[2]) else None] += 1
    for r in list(rem):
        # find add matching r + suffix
        for a in add:
            if a[:2] == r[:2] and SUF.sub("", a[2]) == r[2]:
                cats["suffix_only"].append(k); reasons[SUF.search(a[2]).group(1)] += 1
                add.remove(a); rem.remove(r); break
    for r in list(rem):
        for a in add:
            if a[:2] != r[:2]: continue
            na = SUF.sub("", a[2]); m = SUF.search(a[2])
            if na.replace("SI_TYPE_INVALID", "SI_INTERNAL_DEFECT").replace(re.search(r" \[root-0/[^\]]*\]", na).group(0) if re.search(r" \[root-0/[^\]]*\]", na) else "@@", "") == r[2].replace(re.search(r" \[root-0/[^\]]*\]", r[2]).group(0) if re.search(r" \[root-0/[^\]]*\]", r[2]) else "@@", ""):
                cats["code_or_location"].append((k, r, a)); reasons[m.group(1) if m else None] += 1
                add.remove(a); rem.remove(r); break
    for r in rem: cats["other_removed"].append((k, r))
    for a in add: cats["other_added"].append((k, a))
for c, v in cats.items(): print(c, len(v))
print("suffix reasons", sorted(reasons.items()))
print("stub reasons", stub_reasons, "stub warnings on runs with result", stub_on)
print("roots with stub warnings", len({k for k, _ in cats["stub"]}))
for c in ("code_or_location", "other_removed", "other_added"):
    for x in cats[c]: print(c, x)
# loggers/levels in diffs
