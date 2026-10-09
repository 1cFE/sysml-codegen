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


@pytest.mark.parametrize(('fixture', 'template'), [
    ('attr_expr_probe', 'teax_module.py.jinja2'),
    ('attr_expr_probe', 'multioutput_model.py.jinja2'),
    ('agg_literal_probe', 'pipeline_yaml.jinja2'),
    ('constraint_multi_instance', 'constraint_module.py.jinja2'),
    ('constraint_multi_instance', 'report_aggregator.py.jinja2'),
])
def test_oracle_rejects_template_mutation(fixture, template, tmp_path, monkeypatch):
    """Change emitted bytes in each package shape while leaving fixed expectations intact."""
    import jinja2
    import sysml_codegen.cli as cli

    original = cli._get_template_env

    def changed_environment():
        env = original()
        text, _, _ = env.loader.get_source(env, template)
        env.loader = jinja2.ChoiceLoader([
            jinja2.DictLoader({template: text + '\n# deliberate oracle mutation\n'}),
            env.loader,
        ])
        return env

    monkeypatch.setattr(cli, '_get_template_env', changed_environment)
    relative = f'tests/fixtures/{fixture}/instance_graph_snapshot.json'
    actual = public_result(ROOT / relative, tmp_path / 'package')
    assert actual['success']
    with pytest.raises(AssertionError):
        assert actual == BASELINE['snapshots'][relative]['result']


def test_oracle_rejects_rendering_code_mutation(tmp_path, monkeypatch):
    import sysml_codegen.generation as generation

    original = generation.generate_teax_module

    def changed_rendering(*args, **kwargs):
        return original(*args, **kwargs) + '\n# deliberate rendering mutation\n'

    monkeypatch.setattr(generation, 'generate_teax_module', changed_rendering)
    relative = 'tests/fixtures/attr_expr_probe/instance_graph_snapshot.json'
    actual = public_result(ROOT / relative, tmp_path / 'package')
    assert actual['success']
    with pytest.raises(AssertionError):
        assert actual == BASELINE['snapshots'][relative]['result']
