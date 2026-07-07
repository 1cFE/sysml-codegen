"""Item A: sanitize_name injectivity + isidentifier probes (no license needed)."""

from sysml_codegen.core.qualified_names import sanitize_name

print("=" * 60)
print("A1: INJECTIVITY — sibling names colliding on same output")
print("=" * 60)
colliding_pairs = [
    ("a b", "a-b"),
    ("a.b", "a_b"),
    ("a&b", "a$b"),
    ("net electric", "net-electric"),
    ("x@y", "x#y"),
    ("'wall type'", "wall-type"),
]
for lhs, rhs in colliding_pairs:
    ol, orr = sanitize_name(lhs), sanitize_name(rhs)
    verdict = "COLLIDE" if ol == orr else "distinct"
    print(f"  {lhs!r:20} -> {ol!r:16} | {rhs!r:20} -> {orr!r:16}  [{verdict}]")

print()
print("=" * 60)
print("A2: ISIDENTIFIER — output must always be a valid identifier")
print("=" * 60)
candidates = [
    "2nd stage",       # leading digit (quoted SysML name)
    "3phase",          # leading digit
    "class",           # covered keyword
    "def",             # covered keyword
    "return",          # covered keyword
    "import",          # keyword covered
    "for",             # python keyword NOT in guard set
    "while",           # python keyword NOT in guard set
    "if",              # python keyword NOT in guard set
    "None",            # python keyword NOT in guard set
    "True",            # python keyword NOT in guard set
    "lambda",          # python keyword NOT in guard set
    "global",          # python keyword NOT in guard set
    "",                # empty
    "!!!",             # all-symbols
    "@#$",             # all-symbols
    "123",             # pure digits
    "'99 bottles'",    # leading digit quoted
]
fails = []
for c in candidates:
    out = sanitize_name(c)
    ok = out.isidentifier()
    kw_note = ""
    import keyword
    if keyword.iskeyword(out):
        kw_note = " [IS-PYTHON-KEYWORD]"
    if not ok or kw_note:
        fails.append((c, out, ok, keyword.iskeyword(out)))
    flag = "" if (ok and not keyword.iskeyword(out)) else "  <<< PROBLEM"
    print(f"  {c!r:16} -> {out!r:16} isidentifier={ok}{kw_note}{flag}")

print()
print("FAILURES (non-identifier OR python keyword):")
for c, out, ok, iskw in fails:
    reason = []
    if not ok:
        reason.append("not-identifier")
    if iskw:
        reason.append("python-keyword")
    print(f"  {c!r} -> {out!r}  ({', '.join(reason)})")
