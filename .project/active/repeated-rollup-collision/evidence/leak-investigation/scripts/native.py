import sys, glob, syside
paths = sorted(glob.glob(sys.argv[1] + "/**/*.sysml", recursive=True))
model, diag = syside.load_model(paths)
print("errors:", diag.contains_errors() if hasattr(diag,'contains_errors') else diag)
comp = syside.Compiler()
els = {}
for el in model.elements(syside.Feature, include_subtypes=True):
    qn = el.qualified_name
    if qn is not None:
        els[str(qn)] = el
top = els["P::top"]
for name in ["ac", "bc", "cc", "av", "bv", "capital_cost"]:
    f = els.get(f"P::Top::{name}")
    if f is None: continue
    r, rep = comp.evaluate_feature(feature=f, scope=top)
    print(name, r, "" if rep else rep.diagnostics)
