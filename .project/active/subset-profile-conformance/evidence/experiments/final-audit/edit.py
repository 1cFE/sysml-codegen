import sys, pathlib
def edit(path, old, new, count=1):
    p = pathlib.Path(path); s = p.read_text()
    n = s.count(old)
    assert n >= 1, f"{path}: pattern not found: {old!r}"
    p.write_text(s.replace(old, new, count)); print(f"edited {path} ({n} matches, replaced {count})")
