"""Trace every codegen account site over every case's generator half; print reached rows by role."""
import json, sys, collections
from tests.helpers.subset_profile import cases, mutate, observe, site_scan

rows = site_scan.load_account().rows
targets, refused = {}, {}
for r in rows:
    try:
        t = mutate.site_target(r.site_id)
        with mutate.recording_fired({r.site_id: t}):
            pass
        targets[r.site_id] = t
    except Exception as e:  # report and skip: experiment only
        refused[r.site_id] = f"{type(e).__name__}: {e}"
print("untraceable:", len(refused))
for k, v in refused.items():
    print("  ", k, v)
fired = {}
for a in cases.all_answers():
    with mutate.recording_fired(targets) as seen:
        observe.generator_half(cases.model_root(a)).run()
    fired[a.case_id] = sorted(seen)
by_site = collections.defaultdict(list)
for c, s in fired.items():
    for x in s:
        by_site[x].append(c)
role = {r.site_id: r for r in rows}
print("cases:", len(fired))
for sid in sorted(by_site, key=lambda s: role[s].role):
    r = role[sid]
    print(r.role.value, sid, len(by_site[sid]), by_site[sid][:3])
json.dump(fired, open("/tmp/af2a/fired.json", "w"), indent=1)
