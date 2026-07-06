"""SC-4 A1 — entry-point key uniqueness fail-fast (PIPELINE-TRUTH Item 5, INV-5).

sanitize_name is many-to-one, so two distinct sibling SysML names can collapse to
one entry-point key and silently overwrite each other. The guard at key
construction (extract_design_attributes, where the raw names still exist) raises
instead. Channels are already covered by OutputRegistry.register_scoped.
"""

from __future__ import annotations

import pytest

from sysml_codegen.analysis.parameter_groups import extract_design_attributes
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import requires_license, snapshot_fixture


@requires_license
def test_sc4a1_sibling_key_collision_fails_fast():
    """`'a b'` and `'a-b'` both sanitize to `a_b` — extraction raises, naming the
    two distinct raw names (does not silently keep one)."""
    fixture_dir = snapshot_fixture("ep_key_collision_probe").parent
    ex = SysMLDataExtractor([fixture_dir])
    assert ex.load_models()
    with pytest.raises(ValueError, match="Entry-point key collision"):
        extract_design_attributes(ex.model)
