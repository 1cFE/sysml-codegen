"""Report the exact referent and owner for two candidate bare-reference shapes."""

from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.extractor import SysMLDataExtractor

ROOT = Path(__file__).parent


for case in ("inside-sibling", "parent-scope"):
    extractor = SysMLDataExtractor([ROOT / case])
    loaded = extractor.load_models()
    references = SysideAdapter.elements_of_type(
        extractor.model, "FeatureReferenceExpression", include_subtypes=True
    )
    resolved = []
    for reference in references:
        referent = getattr(reference, "referent", None)
        owner = getattr(referent, "owning_type", None)
        resolved.append(
            (
                str(getattr(referent, "qualified_name", None)),
                str(getattr(owner, "qualified_name", None)),
            )
        )
    print(case, "loaded=", loaded, "resolved=", resolved)
