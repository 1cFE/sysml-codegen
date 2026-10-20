"""Throwaway: a generic, type-tagged JSON codec for SubsetFacts (spike only, not a schema).

Encodes any frozen/plain dataclass, StrEnum, UUID, tuple, list, frozenset, dict, float and
primitive by tagging the Python type, so decode(encode(x)) rebuilds the same objects. It
proves the facts *can* round-trip; a real envelope schema would name fields explicitly.
"""

from __future__ import annotations

import dataclasses
import importlib
import json
import math
from enum import Enum
from typing import Any
from uuid import UUID


def _qual(t: type) -> str:
    return f"{t.__module__}:{t.__qualname__}"


def _load(q: str) -> Any:
    mod, name = q.split(":")
    obj: Any = importlib.import_module(mod)
    for part in name.split("."):
        obj = getattr(obj, part)
    return obj


def to_jsonable(x: Any) -> Any:
    if x is None or isinstance(x, bool) or isinstance(x, str) and not isinstance(x, Enum):
        return x
    if isinstance(x, Enum):
        return {"$e": _qual(type(x)), "v": x.value}
    if isinstance(x, int):
        return x
    if isinstance(x, float):
        if math.isfinite(x):
            return {"$f": x.hex()}  # exact; repr would also do
        return {"$f": repr(x)}
    if isinstance(x, UUID):
        return {"$u": str(x)}
    if dataclasses.is_dataclass(x) and not isinstance(x, type):
        fields = {}
        for f in dataclasses.fields(x):
            fields[f.name] = to_jsonable(getattr(x, f.name))
        return {"$d": _qual(type(x)), "f": fields}
    if isinstance(x, tuple):
        return {"$t": [to_jsonable(i) for i in x]}
    if isinstance(x, list):
        return [to_jsonable(i) for i in x]
    if isinstance(x, frozenset):
        items = [to_jsonable(i) for i in x]
        items.sort(key=lambda i: json.dumps(i, sort_keys=True))
        return {"$fs": items}
    if isinstance(x, dict):
        return {"$m": [[to_jsonable(k), to_jsonable(v)] for k, v in x.items()]}
    raise TypeError(f"unencodable {type(x)!r}: {x!r}")


def from_jsonable(x: Any) -> Any:
    if isinstance(x, list):
        return [from_jsonable(i) for i in x]
    if not isinstance(x, dict):
        return x
    if "$e" in x:
        return _load(x["$e"])(x["v"])
    if "$f" in x:
        v = x["$f"]
        return float.fromhex(v) if not v.endswith(("inf", "nan")) else float(v)
    if "$u" in x:
        return UUID(x["$u"])
    if "$t" in x:
        return tuple(from_jsonable(i) for i in x["$t"])
    if "$fs" in x:
        return frozenset(from_jsonable(i) for i in x["$fs"])
    if "$m" in x:
        return {from_jsonable(k): from_jsonable(v) for k, v in x["$m"]}
    if "$d" in x:
        cls = _load(x["$d"])
        values = {k: from_jsonable(v) for k, v in x["f"].items()}
        init = {f.name for f in dataclasses.fields(cls) if f.init}
        obj = cls(**{k: v for k, v in values.items() if k in init})
        for k, v in values.items():
            if k not in init and getattr(obj, k) != v:
                raise ValueError(f"{cls}: non-init field {k} differs: {getattr(obj, k)!r} != {v!r}")
        return obj
    raise ValueError(f"untagged object {list(x)[:5]}")


def encode(x: Any) -> str:
    return json.dumps(to_jsonable(x), sort_keys=True, separators=(",", ":"), allow_nan=False)


def decode(s: str) -> Any:
    return from_jsonable(json.loads(s))
