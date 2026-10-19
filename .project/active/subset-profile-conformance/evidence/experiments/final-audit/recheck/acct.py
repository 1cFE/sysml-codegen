import csv, io
def set_row(site_prefix, **cols):
    p="sysml-codegen/tests/expectations/subset_profile/site_account.csv"
    lines=open(p).read().splitlines(keepends=True)
    head=[l for l in lines if l.startswith("#")]; body="".join(l for l in lines if not l.startswith("#"))
    rows=list(csv.reader(io.StringIO(body))); hdr=rows[0]; n=0
    for r in rows[1:]:
        if r[0].startswith(site_prefix):
            for k,v in cols.items(): r[hdr.index(k)]=v
            n+=1
    assert n==1, n
    out=io.StringIO(); csv.writer(out, lineterminator="\n").writerows(rows)
    open(p,"w").write("".join(head)+out.getvalue()); print("row edited", site_prefix, cols)
