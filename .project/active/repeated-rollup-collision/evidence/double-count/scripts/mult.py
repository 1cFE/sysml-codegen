import sys, glob, syside
model, diag = syside.load_model(sorted(glob.glob(sys.argv[1] + "/**/*.sysml", recursive=True)))
for el in model.elements(syside.PartUsage, include_subtypes=True):
    qn = str(el.qualified_name)
    if qn.startswith("s::"):
        m = el.multiplicity
        print(qn, "owned multiplicity:", None if m is None else (getattr(m,'lower_bound',None), getattr(m,'upper_bound',None)))
