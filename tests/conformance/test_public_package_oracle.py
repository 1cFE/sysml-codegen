"""Independent complete-output oracle captured before cleanup source changes."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.helpers.public_package_oracle import public_result, tree_sha256

ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = ROOT / 'tests/expectations/public_package_oracle/baseline.json'
BASELINE = json.loads(BASELINE_PATH.read_text())


def test_baseline_inventory_is_complete() -> None:
    actual = {path.relative_to(ROOT).as_posix() for path in (ROOT / 'tests/fixtures').rglob('instance_graph_snapshot.json')}
    assert set(BASELINE['snapshots']) == actual
    assert len(actual) == 22


@pytest.mark.parametrize('relative', sorted(BASELINE['snapshots']))
def test_public_package_matches_independent_baseline(relative: str, tmp_path: Path) -> None:
    expected = BASELINE['snapshots'][relative]['result']
    allowances_path = BASELINE_PATH.with_name('reviewed_changes.json')
    if allowances_path.exists():
        changes = json.loads(allowances_path.read_text()).get(relative, {})
        expected = dict(expected, files=dict(expected['files']))
        for path, change in changes.items():
            assert expected['files'][path] == change['old_sha256']
            expected['files'][path] = change['new_sha256']
    output = tmp_path / 'package'
    assert public_result(ROOT / relative, output) == expected
    if not expected['success']:
        assert not output.exists()
        output.mkdir()
        (output / 'sentinel.txt').write_bytes(b'owner handwritten bytes\n')
        before = tree_sha256(output)
        assert public_result(ROOT / relative, output) == expected
        assert tree_sha256(output) == before
