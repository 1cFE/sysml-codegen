#!/usr/bin/env python3
"""Join the per-item spine records into one chronological history document."""
import json, pathlib, collections, sys

SCRATCH = pathlib.Path(__file__).parent
SPINE = SCRATCH / "spine"
OUT = pathlib.Path("/home/reid/1cfe/sysml-codegen/.project/active/decision-harvest/execution-history.md")

recs, bad = [], []
for f in sorted(SPINE.glob("*.json")):
    try:
        r = json.loads(f.read_text())
        r.setdefault("dir", f.stem)
        recs.append(r)
    except Exception as e:
        bad.append((f.name, str(e)))

def key(r):
    return (r.get("date_start") or r.get("date_end") or "0000-00-00", r.get("dir", ""))

recs.sort(key=key)

# group by epic, ordered by each epic's earliest item
by_epic = collections.defaultdict(list)
for r in recs:
    by_epic[(r.get("epic") or "unknown").strip() or "unknown"].append(r)
epic_order = sorted(by_epic, key=lambda e: key(by_epic[e][0]))

def fmt_list(items, indent="  "):
    items = [i for i in (items or []) if str(i).strip()]
    return "\n".join(f"{indent}- {i}" for i in items) if items else f"{indent}- (none stated)"

lines = []
lines.append("# Execution History — `.project/completed/`\n")
lines.append("Reconstructed chronology of every archived work item. One record per folder,\n"
             "produced by a per-folder summarization pass and joined mechanically.\n"
             "Ordered by epic, earliest first; items within an epic ordered by date.\n")
lines.append(f"**Items**: {len(recs)}  |  **Epics (incl. `unknown`)**: {len(epic_order)}\n")

# ---- timeline table ----
lines.append("\n## Timeline\n")
lines.append("| ID | Date | Epic | Item | Subject | Title | Status |")
lines.append("|---|---|---|---|---|---|---|")
for r in recs:
    d = r.get("date_end") or r.get("date_start") or "?"
    lines.append("| {} | {} | {} | {} | {} | {} | {} |".format(
        r.get("id","?"), d, r.get("epic", "unknown"), r.get("item_number") or "—",
        r.get("subject", ""), (r.get("title", "") or "").replace("|", "\\|"),
        r.get("status", "unknown")))

# ---- per-epic detail ----
lines.append("\n---\n\n## By Epic\n")
for e in epic_order:
    items = by_epic[e]
    span = f"{items[0].get('date_start') or items[0].get('date_end')} → {items[-1].get('date_end')}"
    lines.append(f"\n### {e}  \n*{len(items)} item(s), {span}*\n")
    for r in items:
        lines.append(f"\n#### {r.get('id','?')} · {r.get('date_end','?')} — {r.get('item_number') or ''} {r.get('title','')}".rstrip())
        lines.append(f"`{r.get('dir')}`  ·  subject: **{r.get('subject','')}**  ·  status: **{r.get('status','unknown')}**\n")
        lines.append(r.get("summary", "").strip() + "\n")
        lines.append("**Key decisions**")
        lines.append(fmt_list(r.get("key_decisions")))
        sup = [s for s in (r.get("supersedes") or []) if str(s).strip()]
        if sup:
            lines.append("\n**Supersedes / retires**")
            lines.append(fmt_list(sup))

# ---- supersession chain ----
lines.append("\n---\n\n## Supersession Index\n")
lines.append("Every item that explicitly replaced, retired, or deleted earlier work.\n")
any_sup = False
for r in recs:
    sup = [s for s in (r.get("supersedes") or []) if str(s).strip()]
    if sup:
        any_sup = True
        lines.append(f"\n**{r.get('id','?')} · {r.get('date_end','?')} — {r.get('dir')}** ({r.get('epic','unknown')})")
        lines.append(fmt_list(sup))
if not any_sup:
    lines.append("\n(none recorded)")

if bad:
    lines.append("\n---\n\n## Unparseable records\n")
    for n, e in bad:
        lines.append(f"- `{n}`: {e}")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n")
print(f"records: {len(recs)}  epics: {len(epic_order)}  unparseable: {len(bad)}")
print(f"wrote: {OUT}  ({len(lines)} lines)")
