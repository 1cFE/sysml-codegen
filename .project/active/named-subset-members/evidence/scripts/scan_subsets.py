"""List user part usages that subset (not redefine) another user part usage, per model root."""
import sys, logging
from pathlib import Path
logging.disable(logging.CRITICAL)
import syside
from tests.conftest import FIXTURES_DIR
from tests.helpers.refusal_cases.fixture_classes import model_roots
roots = [FIXTURES_DIR / k for k in sorted(model_roots())] + [Path(p) for p in sys.argv[1:]]
for root in roots:
    files = sorted(str(f) for f in root.rglob("*.sysml"))
    try:
        model, diag = syside.load_model(files)
    except Exception as e:
        print(root, "LOAD FAIL", e); continue
    user = set(files)
    hits = []
    for u in model.elements(syside.PartUsage, include_subtypes=True):
        if u.qualified_name is None: continue
        for rel in (u.owned_subsettings or []):
            if isinstance(rel, (syside.Redefinition, syside.ReferenceSubsetting)): continue
            tgt = rel.subsetted_feature
            if tgt is None: continue
            chain = list(getattr(tgt, "chaining_features", ()) or ())
            end = chain[-1] if chain else tgt
            if not isinstance(end, syside.PartUsage) or end.qualified_name is None: continue
            if str(end.qualified_name).split("::")[0] in ("Parts","Items","Occurrences","Objects","Base","Systems"): continue
            uo = u.owning_type or u.owner; to = end.owning_type or end.owner
            m = end.multiplicity
            hits.append(f"  {u.qualified_name} :> {end.qualified_name}{' [chain]' if chain else ''} | owners {type(uo).__name__}:{getattr(uo,'name',None)} / {type(to).__name__}:{getattr(to,'name',None)} | target mult {'own' if m is not None else 'none'}")
    if hits:
        print(str(root).replace(str(FIXTURES_DIR)+"/", ""))
        print("\n".join(hits))
