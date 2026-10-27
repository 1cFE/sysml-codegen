"""Find part usages that subset (not redefine) another user part usage. usage: scan.py root..."""
import sys, json
from pathlib import Path
import syside
def roots_of(p):
    p = Path(p)
    if any(p.glob("*.sysml")): return [p]
    subs = [d for d in sorted(p.iterdir()) if d.is_dir() and any(d.rglob("*.sysml"))]
    return subs if subs and not any(p.glob("*.sysml")) else [p]
out = {}
for line in open(sys.argv[1]):
    arg, cls = line.rstrip("\n").split("\t")
    for root in [Path(arg)]:
        files = sorted(str(f) for f in root.rglob("*.sysml"))
        if not files: continue
        try:
            model, diag = syside.load_model(files)
        except Exception as e:
            out[str(root)] = f"load failed {e}"; continue
        user = {str(f) for f in files}
        hits = []
        for u in model.elements(syside.PartUsage, include_subtypes=False):
            if u.qualified_name is None: continue
            for rel in (u.owned_subsettings or []):
                if isinstance(rel, (syside.Redefinition, syside.ReferenceSubsetting)): continue
                tgt = rel.subsetted_feature
                if tgt is None or not isinstance(tgt, syside.PartUsage) or tgt.qualified_name is None: continue
                if str(tgt.qualified_name).split("::")[0] in ("Parts","Items","Occurrences","Objects","Base"): continue
                m = tgt.multiplicity
                hits.append(f"{u.qualified_name} :> {tgt.qualified_name} (target owned mult {'yes' if m is not None else 'none'})")
        if hits: out[str(root)] = {"class": cls, "hits": hits}
print(json.dumps(out, indent=1))
