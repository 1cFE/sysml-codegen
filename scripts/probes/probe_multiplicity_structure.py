#!/usr/bin/env python3
"""Probe 4: Map multiplicity structure on PartUsages within PartDefs.

For each PartDef in solar_battery, finds child PartUsages with multiplicity.
Prints the complete multiplicity structure including:
- Part name and child name
- multiplicity object type and all accessible attributes
- cached_lower_bound and cached_upper_bound (and whether they match)
- upper_bound chain (referent.name, referent.feature_value_expression)

Key questions:
- Does cached_lower_bound == the SysML declared count (e.g., 20)?
- Does cached_upper_bound == count + 1 (exclusive upper bound)?
- Does upper_bound.referent.name resolve to the count attribute (e.g., "module_count")?
- Does upper_bound.referent.feature_value_expression contain the default value?

Usage:
    uv run python scripts/probes/probe_multiplicity_structure.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from sysml_codegen.extraction.extractor import SysMLDataExtractor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_attr(obj: Any, attr: str, default: Any = "<missing>") -> Any:
    """Safely access attribute."""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def type_name(obj: Any) -> str:
    """Return type(obj).__name__."""
    if obj is None or obj == "<missing>":
        return "<None>"
    return type(obj).__name__


def sanitize_name(name: str | None) -> str:
    """Strip quotes, replace spaces."""
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    return name


def dump_all_attrs(obj: Any, prefix: str = "    ", exclude: set[str] | None = None) -> None:
    """Dump all accessible attributes of an object for discovery."""
    if obj is None or obj == "<missing>":
        print(f"{prefix}<None>")
        return

    exclude = exclude or set()
    # Try common known attributes first
    known_attrs = [
        "lower_bound", "upper_bound", "cached_lower_bound", "cached_upper_bound",
        "has_cached_bounds", "bounds", "bound", "name", "qualified_name",
        "owned_members", "owned_relationships", "owner", "owning_type",
        "referent", "feature_value_expression", "value", "natural_value",
        "is_default", "direction", "multiplicity",
    ]

    for attr in known_attrs:
        if attr in exclude:
            continue
        val = safe_attr(obj, attr)
        if val == "<missing>":
            continue

        if isinstance(val, (str, int, float, bool, type(None))):
            print(f"{prefix}.{attr}: {val!r}")
        elif hasattr(val, "__iter__") and not isinstance(val, str):
            try:
                items = list(val)
                if items:
                    print(f"{prefix}.{attr}: [{len(items)} items]")
                    for i, item in enumerate(items[:3]):
                        print(f"{prefix}  [{i}] {type_name(item)} name={safe_attr(item, 'name')!r}")
                else:
                    print(f"{prefix}.{attr}: []")
            except (TypeError, AttributeError):
                print(f"{prefix}.{attr}: {type_name(val)}")
        else:
            print(f"{prefix}.{attr}: {type_name(val)} name={safe_attr(val, 'name')!r}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("Probe 4: Multiplicity Structure on PartUsages")
    print("=" * 70)

    model_path = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "solar_battery_model"

    print(f"\nLoading model from: {model_path}")
    try:
        extractor = SysMLDataExtractor([model_path])
        if not extractor.load_models():
            print("  ERROR: load_models() returned False", file=sys.stderr)
            sys.exit(1)
        model = extractor.model
        adapter = extractor.adapter
        print("  Model loaded successfully")
    except Exception as e:
        print(f"  ERROR loading model: {e}", file=sys.stderr)
        sys.exit(1)

    total_with_mult = 0
    total_without_mult = 0

    for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
        part_name = sanitize_name(safe_attr(part_def, "name", ""))

        children_with_mult = []
        children_without_mult = []

        for member in getattr(part_def, "owned_members", []):
            if not SysideAdapter.is_instance(member, "PartUsage"):
                continue

            child_name = sanitize_name(safe_attr(member, "name", ""))
            mult = getattr(member, "multiplicity", None)

            if mult is not None:
                children_with_mult.append((child_name, member, mult))
            else:
                children_without_mult.append(child_name)

        if not children_with_mult and not children_without_mult:
            continue

        print(f"\n{'=' * 60}")
        print(f"PartDef: {part_name}")
        print(f"  Children with multiplicity: {len(children_with_mult)}")
        print(f"  Children without multiplicity (singletons): {len(children_without_mult)}")

        if children_without_mult:
            print(f"  Singletons: {', '.join(children_without_mult)}")

        for child_name, member, mult in children_with_mult:
            total_with_mult += 1
            print(f"\n  --- {child_name} (has multiplicity) ---")

            # Get the typing info for the child
            try:
                child_types = list(member.types)
                if child_types:
                    ct = child_types[0]
                    print(f"    typed by: {type_name(ct)} name={safe_attr(ct, 'name')!r}")
            except (TypeError, AttributeError):
                pass

            # Multiplicity object
            print(f"    multiplicity object type: {type_name(mult)}")

            # All multiplicity attributes
            print(f"    multiplicity attributes:")
            dump_all_attrs(mult, prefix="      ")

            # Specific checks
            cached_lower = safe_attr(mult, "cached_lower_bound")
            cached_upper = safe_attr(mult, "cached_upper_bound")
            print(f"\n    KEY VALUES:")
            print(f"      cached_lower_bound: {cached_lower!r} (type: {type(cached_lower).__name__ if cached_lower != '<missing>' else 'N/A'})")
            print(f"      cached_upper_bound: {cached_upper!r} (type: {type(cached_upper).__name__ if cached_upper != '<missing>' else 'N/A'})")

            if cached_lower != "<missing>" and cached_upper != "<missing>":
                try:
                    lower_int = int(cached_lower)
                    upper_int = int(cached_upper)
                    delta = upper_int - lower_int
                    print(f"      upper - lower = {delta} (expected: 1 if exclusive upper bound)")
                except (ValueError, TypeError):
                    print(f"      Cannot compare bounds as integers")

            # Probe upper_bound chain in detail
            upper_bound = safe_attr(mult, "upper_bound")
            if upper_bound not in (None, "<missing>"):
                print(f"\n    upper_bound chain:")
                print(f"      type: {type_name(upper_bound)}")
                dump_all_attrs(upper_bound, prefix="        ", exclude={"owned_members", "owned_relationships"})

                # Follow referent chain
                referent = safe_attr(upper_bound, "referent")
                if referent not in (None, "<missing>"):
                    print(f"      referent:")
                    print(f"        type: {type_name(referent)}")
                    print(f"        name: {safe_attr(referent, 'name')!r}")
                    print(f"        qualified_name: {safe_attr(referent, 'qualified_name')!r}")

                    # Check if referent has a default value
                    fve = safe_attr(referent, "feature_value_expression")
                    if fve not in (None, "<missing>"):
                        print(f"        feature_value_expression: {type_name(fve)}")
                        fve_value = safe_attr(fve, "value")
                        fve_natural = safe_attr(fve, "natural_value")
                        print(f"          .value: {fve_value!r}")
                        print(f"          .natural_value: {fve_natural!r}")

                    # Check referent's owner (should be the same PartDef)
                    ref_owner = safe_attr(referent, "owning_type")
                    if ref_owner not in (None, "<missing>"):
                        print(f"        owning_type: {type_name(ref_owner)} name={safe_attr(ref_owner, 'name')!r}")

                    # Check feature_value for is_default
                    fv = safe_attr(referent, "feature_value")
                    if fv not in (None, "<missing>"):
                        is_default = safe_attr(fv, "is_default")
                        print(f"        feature_value.is_default: {is_default!r}")

            # Probe lower_bound chain
            lower_bound = safe_attr(mult, "lower_bound")
            if lower_bound not in (None, "<missing>"):
                print(f"\n    lower_bound chain:")
                print(f"      type: {type_name(lower_bound)}")
                dump_all_attrs(lower_bound, prefix="        ", exclude={"owned_members", "owned_relationships"})

        total_without_mult += len(children_without_mult)

    # Also check for sibling count attributes (AttributeUsage with integer defaults)
    print(f"\n{'=' * 70}")
    print("Count Attributes (sibling attributes that multiplicity references)")
    print(f"{'=' * 70}")

    for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
        part_name = sanitize_name(safe_attr(part_def, "name", ""))

        count_attrs = []
        for member in getattr(part_def, "owned_members", []):
            if not SysideAdapter.is_instance(member, "AttributeUsage"):
                continue
            member_name = sanitize_name(safe_attr(member, "name", ""))
            if "count" in member_name.lower():
                count_attrs.append(member)

        if count_attrs:
            print(f"\n  {part_name}:")
            for attr in count_attrs:
                attr_name = sanitize_name(safe_attr(attr, "name", ""))
                expr = getattr(attr, "feature_value_expression", None)
                fv = safe_attr(attr, "feature_value")
                is_default = safe_attr(fv, "is_default") if fv not in (None, "<missing>") else "N/A"

                value = "<none>"
                if expr is not None:
                    raw_val = safe_attr(expr, "value")
                    if raw_val not in ("<missing>",):
                        value = repr(raw_val)

                print(f"    {attr_name}: value={value}, is_default={is_default}")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  PartUsages with multiplicity: {total_with_mult}")
    print(f"  PartUsages without multiplicity (singletons): {total_without_mult}")

    # Verify our hierarchy_resolver produces correct MultiplicityData
    print(f"\n--- Verifying hierarchy_resolver output ---")
    try:
        from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
        hierarchy = extract_hierarchy_data(model)

        print(f"  MultiplicityData count: {len(hierarchy.multiplicities)}")
        for md in hierarchy.multiplicities:
            print(f"    {md.owning_part_def_qn}.{md.part_usage_name}:")
            print(f"      count={md.count}, count_attr={md.count_attribute_name}, default={md.default_value}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
