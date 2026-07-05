"""Design-time node-shape probe for SC-3 (retyped part usages).

Confirms:
  Q1  usage.types ordering for a retyped usage (declared type last?)
  Q2  owned FeatureTyping targets via heritage — how many, in what order,
      and are they OWNED-only or do they include inherited-chain typings?
  Q3  most-specific ordering signal available to compare multiple typings.
"""
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.core.qualified_names import build_element_qualified_name

MODEL = Path(__file__).parent / "model.sysml"

ex = SysMLDataExtractor([MODEL])
assert ex.load_models(), "load failed"
model = ex.model

for usage in SysideAdapter.elements_of_type(model, "PartUsage"):
    name = getattr(usage, "name", "?")
    owner = getattr(usage, "owning_type", None)
    owner_qn = build_element_qualified_name(owner) if owner is not None else None
    print(f"\n=== PartUsage name={name!r}  owner={owner_qn}")

    # Q1 — .types ordering
    try:
        types = list(usage.types)
    except Exception as e:  # noqa: BLE001
        types = []
        print("  types EXC", e)
    print("  usage.types order:", [getattr(t, "name", "?") for t in types])

    # Q2 — heritage FeatureTyping targets (owned?)
    ft_targets = []
    if hasattr(usage, "heritage"):
        for rel, target in usage.heritage:
            if SysideAdapter.is_instance(rel, "FeatureTyping"):
                ft_targets.append(
                    (getattr(target, "name", "?"),
                     build_element_qualified_name(target))
                )
    print("  heritage FeatureTyping targets:", ft_targets)

    # Q2b/Q3 — is there an owned-only relationships accessor distinct from heritage?
    for attr in ("owned_relationships", "owned_specializations", "own_heritage",
                 "declared_type", "typing", "owned_typings"):
        if hasattr(usage, attr):
            print(f"  has attr {attr!r} ->", type(getattr(usage, attr)))

# Q4 — does elements_of_type("PartDefinition") exclude the standard library?
# If 'Part' (or any KerML/ISQ base) appears, the user_qn_set intersection is NOT
# a sufficient filter and we must fall back to source-document filtering.
part_defs = list(SysideAdapter.elements_of_type(model, "PartDefinition"))
names = sorted(getattr(pd, "name", "?") for pd in part_defs)
print("\n=== elements_of_type(PartDefinition):", names)
print("    includes library base 'Part'? ->", "Part" in names)
