#!/usr/bin/env python3
"""Spike probe (SOURCE-IDENTITY Item 1): SysIDE referents per binding authoring form.

Loads each probe model in ``models/`` separately (a parse failure in one form must
not poison another) and records, for every calc-usage input parameter with a bound
expression:

- the written reference text (recovered from the CST byte span);
- the SysIDE expression node type;
- the resolved referent: qualified name, element type, owning namespace;
- for feature chains: every segment's referent;
- load diagnostics for the model.

Evidence discipline: every referent field below is read directly off SysIDE AST
nodes via the adapter's load surface — NOT through sysml_codegen extraction, so no
field is inferred from the implementation under test. The sysml-codegen extractor's
view of the same bindings is appended separately, clearly labeled, as a comparison
column only.

Occurrence evidence: all AttributeUsage elements and their value expressions are
dumped too, so the concrete-occurrence ``:>> R = 12.7`` capture is visible in the
same raw record.

Usage (license required; run as a script, not ``python -c``):
    set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
    uv run python .project/active/source-identity-binding-semantics-spike/probes/probe_referents.py

Raw JSON output is retained in ``raw/<model>.json``; a human-readable transcript
goes to stdout.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

SPIKE_DIR = Path(__file__).resolve().parent
MODELS_DIR = SPIKE_DIR / "models"
RAW_DIR = SPIKE_DIR / "raw"

_SOURCE_CACHE: dict[str, bytes] = {}


def safe(obj: Any, attr: str) -> Any:
    try:
        return getattr(obj, attr, None)
    except Exception as exc:  # noqa: BLE001 - probe must keep going and record
        return f"<error: {exc}>"


def type_name(obj: Any) -> str:
    return type(obj).__name__ if obj is not None else "<None>"


def syside_qn(elem: Any) -> str | None:
    """SysIDE's own qualified name if exposed, else an owner-chain walk with ``::``.

    The owner-chain fallback uses raw ``name`` values (no sanitization) so the
    record stays a SysIDE-level fact.
    """
    if elem is None:
        return None
    qn = safe(elem, "qualified_name")
    if isinstance(qn, str) and qn:
        return qn
    names: list[str] = []
    current = elem
    seen = 0
    while current is not None and seen < 50:
        name = safe(current, "name")
        if isinstance(name, str) and name:
            names.append(name)
        current = safe(current, "owner")
        seen += 1
    return "::".join(reversed(names)) if names else None


def written_text(expr: Any) -> str | None:
    """The expression exactly as written, from the CST byte span."""
    cst = safe(expr, "cst_node")
    if cst is None:
        return None
    start, end = safe(cst, "start_byte"), safe(cst, "end_byte")
    if not isinstance(start, int) or not isinstance(end, int) or end <= start:
        return None
    loc = SysideAdapter.get_source_location(expr)
    if not loc:
        return None
    path = str(loc[0])
    data = _SOURCE_CACHE.get(path)
    if data is None:
        try:
            data = Path(path).read_bytes()
        except OSError:
            return None
        _SOURCE_CACHE[path] = data
    if end > len(data):
        return None
    try:
        return data[start:end].decode("utf-8").strip()
    except UnicodeDecodeError:
        return None


def describe_element(elem: Any) -> dict[str, Any]:
    owner = safe(elem, "owner")
    return {
        "type": type_name(elem),
        "name": safe(elem, "name"),
        "qualified_name": syside_qn(elem),
        "owner_type": type_name(owner),
        "owner_name": safe(owner, "name") if owner is not None else None,
        "owner_qualified_name": syside_qn(owner),
    }


def describe_expression(expr: Any, depth: int = 0) -> dict[str, Any]:
    """Recursively describe an expression node, shallowly bounded."""
    out: dict[str, Any] = {
        "node_type": type_name(expr),
        "written": written_text(expr),
    }
    if depth > 6:
        out["truncated"] = True
        return out

    if SysideAdapter.is_instance(expr, "FeatureReferenceExpression"):
        referent = safe(expr, "referent")
        out["referent"] = describe_element(referent) if referent is not None else None
        return out

    if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
        target = safe(expr, "target_feature")
        out["target_feature"] = (
            describe_element(target) if target is not None else None
        )
        operands = safe(expr, "operands")
        out["operands"] = [
            describe_expression(op, depth + 1) for op in list(operands or [])
        ]
        return out

    # Literals: record the value attribute if present.
    for lit_attr in ("value",):
        val = safe(expr, lit_attr)
        if isinstance(val, (int, float, bool, str)):
            out["literal_value"] = val

    operands = safe(expr, "operands")
    if operands:
        try:
            ops = list(operands)
        except Exception:  # noqa: BLE001
            ops = []
        if ops:
            out["operator"] = safe(expr, "operator")
            out["operands"] = [describe_expression(op, depth + 1) for op in ops]
    return out


def probe_model(model_file: Path) -> dict[str, Any]:
    record: dict[str, Any] = {"model_file": str(model_file)}

    model, diagnostics = SysideAdapter.load_model([model_file])
    diags: list[dict[str, Any]] = []
    for bucket in ("errors", "warnings"):
        for d in list(safe(diagnostics, bucket) or []):
            diags.append({"bucket": bucket, "text": str(d)})
    record["diagnostics"] = diags
    record["contains_errors"] = bool(
        diagnostics.contains_errors() if diagnostics is not None else False
    )
    if record["contains_errors"]:
        # Still attempt the walk: partial models can carry resolvable bindings,
        # and recording what survives is part of the evidence.
        record["note"] = "load reported errors; walk attempted on partial model"

    # --- SysIDE-level binding evidence -------------------------------------
    calc_usages: list[dict[str, Any]] = []
    try:
        for cu in SysideAdapter.elements_of_type(model, "CalculationUsage"):
            cu_rec: dict[str, Any] = {
                "calc_usage": describe_element(cu),
                "params": [],
            }
            for member in list(safe(cu, "owned_members") or []):
                if not (
                    SysideAdapter.is_instance(member, "AttributeUsage")
                    or SysideAdapter.is_instance(member, "ReferenceUsage")
                ):
                    continue
                direction = str(safe(member, "direction"))
                if "In" not in direction and "inout" not in direction.lower():
                    continue
                expr = safe(member, "feature_value_expression")
                cu_rec["params"].append(
                    {
                        "param": describe_element(member),
                        "direction": direction,
                        "binding_expression": (
                            describe_expression(expr) if expr is not None else None
                        ),
                    }
                )
            calc_usages.append(cu_rec)
    except Exception:  # noqa: BLE001
        cu_rec = {"walk_error": traceback.format_exc()}
        calc_usages.append(cu_rec)
    record["calc_usages"] = calc_usages

    # --- Occurrence evidence: every value-carrying feature ------------------
    # A shorthand `:>> R = 12.7` at a part usage parses as a ReferenceUsage, not
    # an AttributeUsage (first-run observation), so sweep both types and record
    # redefinition links where SysIDE exposes them.
    attributes: list[dict[str, Any]] = []
    try:
        for tname in ("AttributeUsage", "ReferenceUsage"):
            for au in SysideAdapter.elements_of_type(model, tname):
                owner = safe(au, "owner")
                expr = safe(au, "feature_value_expression")
                redef: list[dict[str, Any]] = []
                for attr_name in ("redefined_features", "redefinitions"):
                    targets = safe(au, attr_name)
                    if targets is None or isinstance(targets, str):
                        continue
                    try:
                        for t in list(targets):
                            # A Redefinition relationship node exposes the
                            # redefined feature; a plain feature list is itself.
                            feat = safe(t, "redefined_feature")
                            redef.append(
                                {
                                    "via": attr_name,
                                    "target": describe_element(
                                        feat if feat is not None else t
                                    ),
                                }
                            )
                    except TypeError:
                        continue
                attributes.append(
                    {
                        "feature": describe_element(au),
                        "owner_is_calc": type_name(owner)
                        in ("CalculationUsage", "CalculationDefinition"),
                        "value_written": written_text(expr)
                        if expr is not None
                        else None,
                        "value_node_type": type_name(expr)
                        if expr is not None
                        else None,
                        "redefines": redef,
                    }
                )
    except Exception:  # noqa: BLE001
        attributes.append({"walk_error": traceback.format_exc()})
    record["value_features"] = attributes

    # --- Comparison column ONLY: the implementation-under-test's view -------
    try:
        from sysml_codegen.extraction.usage_extractor import (
            extract_calculation_usages,
        )

        impl_view: list[dict[str, Any]] = []
        cu_list, _report = extract_calculation_usages(model)
        for cu_data in cu_list:
            impl_view.append(
                {
                    "usage_qn": cu_data.qualified_name,
                    "bindings": [
                        {
                            "param": b.param_name,
                            "binding_type": str(b.binding_type),
                            "source_path": b.source_path,
                            "raw_expression": b.raw_expression,
                            "written_qualifier": b.stored_source_written_qualifier,
                            "literal_value": b.literal_value,
                        }
                        for b in cu_data.bindings
                    ],
                    "unbound_params": cu_data.unbound_params,
                }
            )
        record["IMPL_VIEW_sysml_codegen_extractor"] = impl_view
    except Exception:  # noqa: BLE001
        record["IMPL_VIEW_sysml_codegen_extractor"] = traceback.format_exc()

    return record


def main() -> int:
    RAW_DIR.mkdir(exist_ok=True)
    model_files = sorted(MODELS_DIR.glob("*.sysml"))
    if not model_files:
        print(f"No models found in {MODELS_DIR}", file=sys.stderr)
        return 1

    failures = 0
    for mf in model_files:
        print(f"\n{'=' * 78}\nPROBE: {mf.name}\n{'=' * 78}")
        try:
            record = probe_model(mf)
        except Exception:  # noqa: BLE001 - a hard load failure is itself evidence
            record = {"model_file": str(mf), "load_error": traceback.format_exc()}
            failures += 1
        out_path = RAW_DIR / f"{mf.stem}.json"
        out_path.write_text(json.dumps(record, indent=2, default=str) + "\n")
        print(json.dumps(record, indent=2, default=str))
        print(f"[raw retained: {out_path}]")

    print(f"\nDone. {len(model_files)} models probed, {failures} hard failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
