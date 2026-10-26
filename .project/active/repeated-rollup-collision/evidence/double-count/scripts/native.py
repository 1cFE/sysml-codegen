"""Native SysIDE evaluation. usage: native.py <models dir> <feature qn>@<scope qn> ..."""
import sys, glob, syside
paths = sorted(glob.glob(sys.argv[1] + "/**/*.sysml", recursive=True))
model, diag = syside.load_model(paths)
print("errors:", diag.contains_errors(), [str(e.message) for e in diag.errors][:3] if diag.contains_errors() else "")
for w in list(diag.warnings)[:5]: print("warn:", w.message)
comp = syside.Compiler()
els = {}
for el in model.elements(syside.Element, include_subtypes=True):
    qn = getattr(el, "qualified_name", None)
    if qn is not None: els[str(qn)] = el
for spec in sys.argv[2:]:
    f, s = spec.split("@")
    feat, scope = els.get(f), els.get(s)
    if feat is None or scope is None:
        print(spec, "MISSING", feat is None, scope is None); continue
    try:
        r, rep = comp.evaluate_feature(feature=feat, scope=scope)
        def show(x):
            if isinstance(x, (list, tuple)): return [show(i) for i in x]
            q = getattr(x, "qualified_name", None)
            return str(q) if q is not None else x
        print(spec, "=>", show(r), "" if rep else [d.message for d in rep.diagnostics])
    except Exception as e:
        print(spec, "EXC", type(e).__name__, e)
