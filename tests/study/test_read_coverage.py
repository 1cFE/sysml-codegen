"""Actual Python opens, imports and route-gate refusals; no public-input proxies.

Moved from fusion-tea ``tests/study/test_read_coverage.py`` at ``b06585709``. teax's declared
sources come from ``TEAX_SIMKIT_PATH``, and integrate's tool identity names the installed
package's paths.
"""
import json
import os
import py_compile
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from sysml_codegen.study import integrate, roots
from sysml_codegen.study import read_coverage as coverage


@pytest.fixture
def observed_route(tmp_path):
    """A probe route over a one-file package; ``tmp_path`` is its project.

    The driver runs with ``SYSML_CODEGEN_PROJECT_ROOT`` naming that project, as integrate's
    ``seam_env`` hands it to every producer. ``env`` is that environment for tests that go
    through ``integrate.execute_baseline``, read when called.
    """
    package = tmp_path / "package"
    (package / "contracts").mkdir(parents=True)
    value = package / "value.json"
    value.write_text('{"value": 3}')
    (package / "contracts/package_contract.json").write_text(json.dumps({
        "artifact_hashes": {"value.json": coverage.digest(value)},
    }))
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{}')
    route = tmp_path / "route"
    route.mkdir()
    out = tmp_path / "out"
    out.mkdir()
    request = SimpleNamespace(route=(route, "probe_route", "execute"), package=package,
                              manifest=manifest, out_dir=out)

    def write(body):
        (route / "probe_route.py").write_text(
            'from pathlib import Path\nimport sys, os, subprocess\n'
            'def execute(out, *, package_dir, manifest_path):\n'
            + ''.join('    ' + line + '\n' for line in body.splitlines())
            + '    return {}\n'
        )

    def with_root():
        return {**os.environ, roots.PROJECT_ROOT_ENV: str(tmp_path)}

    def run(body, env=None, cwd=None, driver=integrate.ROUTE_DRIVER_SOURCE):
        write(body)
        done = subprocess.run([sys.executable, '-c', driver,
                               str(route), 'probe_route', 'execute', str(out),
                               str(package), str(manifest), 'test-token'],
                              text=True, capture_output=True, cwd=cwd,
                              env=with_root() if env is None else env)
        return done, json.loads((out / 'read_coverage.json').read_text())

    return SimpleNamespace(package=package, route=route, manifest=manifest, out=out,
                           request=request, run=run, write=write, env=with_root)


def test_declared_package_manifest_and_source_reads(observed_route):
    done, receipt = observed_route.run('''(package_dir / "value.json").read_text()
manifest_path.read_text()''')
    assert done.returncode == 0, done.stderr
    assert receipt['outcome'] == 'pass'
    assert {'package-seal', 'manifest', 'declared-source'} <= {r['category'] for r in receipt['reads']}


@pytest.mark.parametrize('location', ['package', 'route', 'outside'])
def test_undeclared_actual_data_reads(observed_route, tmp_path, location):
    roots = {'package': observed_route.package, 'route': observed_route.route, 'outside': tmp_path}
    unexpected = roots[location] / 'unexpected.csv'
    unexpected.write_text('changed data')
    done, receipt = observed_route.run(f'Path({str(unexpected)!r}).read_text()')
    assert done.returncode != 0
    assert 'undeclared' in str(receipt['violations'])


@pytest.mark.parametrize('device', ['/dev/urandom', '/dev/random'])
def test_a_kernel_entropy_device_is_a_runtime_read(observed_route, device):
    """B13: reading an entropy device is the runtime's business, like a read under ``sys.prefix``.

    uv's standalone CPython opens ``/dev/urandom`` on the first ``import random``. On the
    station that import happens inside the observed window, and gate 7 refused the route
    with ``undeclared dependency read: /dev/urandom``. The route here opens the device itself,
    so the refusal reproduces on any interpreter.
    """
    done, receipt = observed_route.run(f'open({device!r}, "rb").read(1)')
    assert done.returncode == 0, done.stderr
    assert receipt['outcome'] == 'pass'
    assert receipt['violations'] == []


def test_any_other_device_is_still_an_undeclared_read(observed_route):
    """B13 names exactly two paths; it is not an allowance for ``/dev``."""
    done, receipt = observed_route.run('open("/dev/zero", "rb").read(1)')
    assert done.returncode != 0
    assert receipt['violations'] == ['undeclared dependency read: /dev/zero']


#: integrate's route driver, with the interpreter's built-in time-zone search path replaced by
#: ``TEST_ZONE_ROOT`` first. That path is fixed when the interpreter is built, so replacing the
#: value the observer read is the only way to point it at a test directory.
ZONE_DRIVER_SOURCE = (
    "import os\nfrom pathlib import Path\nfrom sysml_codegen.study import read_coverage\n"
    "read_coverage.INTERPRETER_ZONE_ROOTS = (Path(os.environ['TEST_ZONE_ROOT']),)\n"
    + integrate.ROUTE_DRIVER_SOURCE
)


@pytest.fixture
def zone_search_path(tmp_path, observed_route):
    """A built-in time-zone search path of the test's own, outside every runtime root.

    A directory beside it holds the same file, so the pair tells "the interpreter's own path"
    from "zone-shaped".
    """
    zones, elsewhere = tmp_path.resolve() / 'zones', tmp_path.resolve() / 'elsewhere'
    for root in (zones, elsewhere):
        (root / 'Etc').mkdir(parents=True)
        (root / 'Etc' / 'UTC').write_bytes(b'TZif2')
    env = {**observed_route.env(), 'TEST_ZONE_ROOT': str(zones)}
    return SimpleNamespace(zone=zones / 'Etc' / 'UTC', elsewhere=elsewhere / 'Etc' / 'UTC', env=env)


def test_a_read_under_the_interpreters_zone_search_path_is_a_runtime_read(
        observed_route, zone_search_path):
    """B13: zone data the interpreter itself looks up is the runtime's, like ``sys.prefix``.

    pandas asks dateutil for UTC at import, and dateutil opens ``/usr/share/zoneinfo/UTC``. Under
    uv's standalone CPython that directory is outside ``sys.prefix``, so gate 7 refused the
    station route with ``undeclared dependency read: /usr/share/zoneinfo/Etc/UTC``. Here the
    interpreter's search path is a test directory, so the refusal reproduces on any interpreter.
    """
    done, receipt = observed_route.run(f'open({str(zone_search_path.zone)!r}, "rb").read()',
                                       env=zone_search_path.env, driver=ZONE_DRIVER_SOURCE)
    assert done.returncode == 0, done.stderr
    assert receipt['violations'] == []
    assert {'path': str(zone_search_path.zone), 'category': 'runtime-observed',
            'sha256': coverage.digest(zone_search_path.zone)} in receipt['reads']


def test_zone_shaped_data_off_the_interpreters_search_path_is_still_undeclared(
        observed_route, zone_search_path):
    """B13 follows the interpreter's own search path; it is no allowance for zone-shaped data."""
    done, receipt = observed_route.run(f'open({str(zone_search_path.elsewhere)!r}, "rb").read()',
                                       env=zone_search_path.env, driver=ZONE_DRIVER_SOURCE)
    assert done.returncode != 0
    assert receipt['violations'] == [f'undeclared dependency read: {zone_search_path.elsewhere}']


def test_pythontzpath_does_not_widen_the_runtime_roots(observed_route, tmp_path):
    """Audit F1: the caller's ``PYTHONTZPATH`` must not switch gate 7 off.

    ``zoneinfo.TZPATH`` is ``('/',)`` under ``PYTHONTZPATH=/``. While B13 followed it, every read
    outside the package counted as runtime, so this undeclared read passed. B13 follows the
    interpreter's build-time ``TZPATH``, which that variable does not change.
    """
    unexpected = tmp_path.resolve() / 'unexpected.csv'
    unexpected.write_text('project data')
    done, receipt = observed_route.run(f'Path({str(unexpected)!r}).read_text()',
                                       env={**observed_route.env(), 'PYTHONTZPATH': '/'})
    assert done.returncode != 0
    assert receipt['violations'] == [f'undeclared dependency read: {unexpected}']


def test_the_zone_search_path_keeps_only_absolute_entries():
    """Empty and relative entries name no directory the interpreter could have been built with."""
    setting = os.pathsep.join(['/usr/share/zoneinfo', '', 'relative/zones', '/etc/zoneinfo', ''])
    expected = (Path('/usr/share/zoneinfo'), Path('/etc/zoneinfo'))
    assert coverage.absolute_entries(setting) == expected


def test_symlink_escape(observed_route, tmp_path):
    outside = tmp_path / 'external.json'
    outside.write_text('outside')
    (observed_route.package / 'escape.json').symlink_to(outside)
    done, receipt = observed_route.run('(package_dir / "escape.json").read_text()')
    assert done.returncode != 0
    assert str(outside) in str(receipt['violations'])


@pytest.mark.parametrize('when', ['before', 'after'])
def test_declared_dependency_mutation(observed_route, when):
    read = '(package_dir / "value.json").read_text()'
    write = '(package_dir / "value.json").write_text("mutated")'
    done, receipt = observed_route.run('\n'.join([write, read] if when == 'before' else [read, write]))
    assert done.returncode != 0
    assert 'changed' in str(receipt['violations'])


def test_new_output_can_be_read(observed_route):
    done, receipt = observed_route.run('''(out / "new.json").write_text("new")
(out / "new.json").read_text()''')
    assert done.returncode == 0, done.stderr
    assert any(r['category'] == 'new-output' for r in receipt['reads'])


@pytest.mark.parametrize('mode', ['a', 'r+'])
def test_preexisting_output_write_does_not_admit_old_data(observed_route, mode):
    (observed_route.out / 'old.json').write_text('old')
    done, receipt = observed_route.run(f'''with (out / "old.json").open({mode!r}) as handle:
    handle.write("new")
(out / "old.json").read_text()''')
    assert done.returncode != 0
    assert 'undeclared' in str(receipt['violations'])


@pytest.mark.parametrize('mutate', [False, True])
def test_cached_import_records_actual_cache_and_source(observed_route, mutate):
    source = observed_route.route / 'cached_dependency.py'
    source.write_text('VALUE = 7\n')
    cache = Path(py_compile.compile(str(source), doraise=True))
    original = coverage.digest(cache)
    body = 'import cached_dependency\nassert cached_dependency.VALUE == 7'
    if mutate:
        body += f'\nPath({str(cache)!r}).write_bytes(b"changed cached bytes")'
    done, receipt = observed_route.run(body)
    assert (done.returncode != 0) is mutate
    row = next(row for row in receipt['reads'] if row['path'] == str(cache))
    assert row['category'] == 'bytecode'
    assert row['sha256'] == original
    assert any(row['path'] == str(source) for row in receipt['reads'])
    if mutate:
        assert 'changed after read' in str(receipt['violations'])


def test_sourceless_bytecode_refused(observed_route):
    source = observed_route.route / 'only_cache.py'
    source.write_text('VALUE = 3\n')
    py_compile.compile(str(source), cfile=str(source.with_suffix('.pyc')), doraise=True)
    source.unlink()
    done, receipt = observed_route.run('import only_cache')
    assert done.returncode != 0
    assert 'undeclared' in str(receipt['violations'])


def test_child_process_refused(observed_route):
    done, receipt = observed_route.run('subprocess.run([sys.executable, "-c", "pass"])')
    assert done.returncode != 0
    assert 'child execution' in str(receipt['violations'])


def test_integer_descriptor_is_explicitly_unsupported(observed_route):
    done, receipt = observed_route.run('''fd = os.open(package_dir / "value.json", os.O_RDONLY)
with open(fd) as handle:
    handle.read()''')
    assert done.returncode != 0
    assert 'integer-descriptor' in str(receipt['violations'])


def test_caught_violation_still_refuses_integration(observed_route):
    extra = observed_route.package / 'unlisted.csv'
    extra.write_text('unexpected')
    observed_route.write('''try:
    (package_dir / "unlisted.csv").read_text()
except RuntimeError:
    pass''')
    with pytest.raises(integrate.SeamBlocker) as caught:
        integrate.execute_baseline(observed_route.request, observed_route.env())
    assert caught.value.condition == 'read-coverage-refused'
    receipt = json.loads((observed_route.out / 'read_coverage.json').read_text())
    assert receipt['violations']
    assert caught.value.evidence


@pytest.mark.parametrize('receipt_kind', ['missing', 'malformed', 'stale', 'empty', 'violation'])
def test_integration_rejects_invalid_receipt_even_on_zero_exit(observed_route, monkeypatch, receipt_kind):
    path = observed_route.out / 'read_coverage.json'
    path.write_text('{"outcome":"pass"}')  # Existing evidence cannot satisfy new invocation.

    def fake_producer(argv, env):
        assert not path.exists()
        if receipt_kind == 'malformed':
            path.write_text('not json')
        elif receipt_kind != 'missing':
            document = {'schema_version': coverage.SCHEMA,
                        'invocation': 'old-token' if receipt_kind == 'stale' else argv[-1],
                        'outcome': 'pass', 'route_error': None,
                        'violations': ['caught'] if receipt_kind == 'violation' else [],
                        'reads': [], 'declarations': [], 'limitations': coverage.LIMITATIONS}
            path.write_text(json.dumps(document))
        return subprocess.CompletedProcess(argv, 0, '{}', '')

    monkeypatch.setattr(integrate, 'run_producer', fake_producer)
    with pytest.raises(integrate.SeamBlocker) as caught:
        integrate.execute_baseline(observed_route.request, {})
    assert caught.value.condition == 'read-coverage-refused'


def test_integration_tool_identity_includes_new_dependencies():
    identity = integrate.common.tool_source_digest(integrate.TOOL_SOURCE_FILES)
    assert {'sysml_codegen/study/indicators.py', 'sysml_codegen/study/read_coverage.py'} <= {entry['path'] for entry in identity['files']}


def test_static_gate_rejects_unpinned_pipeline_reference(synthetic_copy, tmp_path):
    package = synthetic_copy.path
    pipeline = next((package / 'pipelines').glob('*.yaml'))
    text = pipeline.read_text()
    # Redirect an actual EntryPoint ref, leaving the manifest glob unchanged.
    import re
    match = re.search(r'\.\./inputs/[^\s\"\']+\.json', text)
    assert match, text
    pipeline.write_text(text.replace(match.group(), '../outside.json', 1))
    (package / 'outside.json').write_text('{}')
    synthetic_copy.repin()
    request = SimpleNamespace(manifest=synthetic_copy.manifest, package=package, out_dir=tmp_path)
    with pytest.raises(integrate.SeamBlocker) as caught:
        integrate.gate_manifest(request, {}, None)
    assert caught.value.condition == 'manifest-stale'
    assert 'not in the manifest' in caught.value.detail


def test_route_failure_preserves_earlier_violation(observed_route):
    observed_route.write('try:\n    (package_dir / "unknown.txt").read_text()\nexcept RuntimeError:\n    pass\nraise ValueError("route failed too")')
    with pytest.raises(integrate.SeamBlocker) as caught:
        integrate.execute_baseline(observed_route.request, observed_route.env())
    receipt = json.loads((observed_route.out / 'read_coverage.json').read_text())
    assert receipt['violations']
    assert receipt['route_error'] == 'ValueError: route failed too'
    assert caught.value.condition == 'read-coverage-refused'


def test_static_gate_produces_coverage_receipt(synthetic_copy, tmp_path):
    request = SimpleNamespace(manifest=synthetic_copy.manifest, package=synthetic_copy.path, out_dir=tmp_path)
    integrate.gate_manifest(request, {}, None)
    receipt = json.loads((tmp_path / 'manifest_read_coverage.json').read_text())
    assert receipt['outcome'] == 'pass'
    assert any('/inputs/' in path for path in receipt['paths'])


@pytest.mark.parametrize('preexisting', [False, True])
def test_atomic_output_rename_preserves_only_new_admission(observed_route, preexisting):
    if preexisting:
        (observed_route.out / 'final.json').write_text('old')
    done, receipt = observed_route.run('''(out / "temp.json").write_text("new")
(out / "temp.json").replace(out / "final.json")
(out / "final.json").read_text()''')
    assert (done.returncode != 0) is preexisting, done.stderr
    assert bool(receipt['violations']) is preexisting


def test_receipt_structural_validation(observed_route):
    done, receipt = observed_route.run('(package_dir / "value.json").read_text()')
    assert done.returncode == 0
    assert coverage.valid_receipt(receipt, 'test-token')
    receipt['reads'] = ['unstructured']
    assert not coverage.valid_receipt(receipt, 'test-token')


def test_declared_dependency_metadata_change(observed_route, monkeypatch, tmp_path):
    teax = tmp_path / 'teax'
    metadata = teax / 'packages/teax-simkit/probe.egg-info/entry_points.txt'
    metadata.parent.mkdir(parents=True)
    metadata.write_text('original')
    monkeypatch.setenv('TEAX_SIMKIT_PATH', str(teax / 'packages/teax-simkit'))
    done, receipt = observed_route.run(f'Path({str(metadata)!r}).read_text()\nPath({str(metadata)!r}).write_text("changed")')
    assert done.returncode != 0
    assert 'changed after read' in str(receipt['violations'])
    assert any(r['category'] == 'declared-dependency-metadata' for r in receipt['reads'])


def test_route_exception_without_coverage_violation_is_could_not_run(observed_route):
    observed_route.write('(package_dir / "value.json").read_text()\nraise ValueError("unsupported physics domain")')
    with pytest.raises(integrate.SeamBlocker) as caught:
        integrate.execute_baseline(observed_route.request, observed_route.env())
    assert caught.value.mode == integrate.COULD_NOT_RUN
    assert caught.value.condition != 'read-coverage-refused'
    receipt = json.loads((observed_route.out / 'read_coverage.json').read_text())
    assert receipt['violations'] == []
    assert 'unsupported physics domain' in receipt['route_error']
    assert caught.value.evidence


@pytest.mark.parametrize('replacement', ['rename', 'replace', 'hardlink', 'symlink'])
def test_output_admission_cannot_survive_old_content_replacement(observed_route, replacement):
    (observed_route.out / 'old.json').write_text('old untracked content')
    moves = {
        'rename': '(out / "old.json").rename(out / "temp.json")',
        'replace': '(out / "old.json").replace(out / "temp.json")',
        'hardlink': 'os.link(out / "old.json", out / "temp.json")',
        'symlink': '(out / "temp.json").symlink_to(out / "old.json")',
    }
    done, receipt = observed_route.run('''(out / "temp.json").write_text("new")
(out / "temp.json").rename(out / "final.json")
''' + moves[replacement] + '\nassert (out / "temp.json").read_text() == "old untracked content"')
    assert done.returncode != 0
    assert 'undeclared' in str(receipt['violations'])


def test_replacement_revokes_current_destination_admission(observed_route):
    (observed_route.out / 'old.json').write_text('old untracked content')
    done, receipt = observed_route.run('''(out / "new.json").write_text("new")
(out / "old.json").replace(out / "new.json")
assert (out / "new.json").read_text() == "old untracked content"''')
    assert done.returncode != 0
    assert 'undeclared' in str(receipt['violations'])


@pytest.mark.parametrize('replacement', ['rename', 'hardlink'])
def test_unlink_revokes_admission_before_old_file_replacement(observed_route, replacement):
    (observed_route.out / 'old.json').write_text('old')
    move = '(out / "old.json").rename(out / "new.json")' if replacement == 'rename' else 'os.link(out / "old.json", out / "new.json")'
    done, receipt = observed_route.run('''(out / "new.json").write_text("new")
(out / "new.json").unlink()
''' + move + '\n(out / "new.json").read_text()')
    assert done.returncode != 0
    assert 'undeclared' in str(receipt['violations'])


def test_directory_move_revokes_descendant_admission(observed_route):
    old = observed_route.out / 'old_dir'
    old.mkdir()
    (old / 'file.json').write_text('old')
    done, receipt = observed_route.run('''(out / "new_dir").mkdir()
(out / "new_dir/file.json").write_text("new")
(out / "new_dir").rename(out / "moved_dir")
(out / "old_dir").rename(out / "new_dir")
(out / "new_dir/file.json").read_text()''')
    assert done.returncode != 0
    assert 'undeclared' in str(receipt['violations'])


def test_delete_then_genuinely_create_new_output_is_admitted(observed_route):
    done, receipt = observed_route.run('''(out / "new.json").write_text("first")
(out / "new.json").unlink()
(out / "new.json").write_text("second")
assert (out / "new.json").read_text() == "second"''')
    assert done.returncode == 0, done.stderr


def test_sqlite_existing_store_refused_by_integration(observed_route):
    import sqlite3
    old = observed_route.out / 'old.db'
    with sqlite3.connect(old) as db:
        db.execute('CREATE TABLE old_data (value TEXT)')
        db.execute("INSERT INTO old_data VALUES ('old contents')")
    observed_route.write('import sqlite3\nwith sqlite3.connect(out / "old.db") as db:\n    db.execute("SELECT * FROM old_data").fetchall()')
    with pytest.raises(integrate.SeamBlocker) as caught:
        integrate.execute_baseline(observed_route.request, observed_route.env())
    assert caught.value.condition == 'read-coverage-refused'
    receipt = json.loads((observed_route.out / 'read_coverage.json').read_text())
    assert 'SQLite store must be new' in str(receipt['violations'])


def test_new_sqlite_store_can_reconnect(observed_route):
    done, receipt = observed_route.run('''import sqlite3
with sqlite3.connect(out / "new.db") as db:
    db.execute("CREATE TABLE new_data (value TEXT)")
with sqlite3.connect(out / "new.db") as db:
    db.execute("SELECT * FROM new_data").fetchall()''')
    assert done.returncode == 0, done.stderr
    assert receipt['admitted_new_sqlite_stores'] == [str(observed_route.out / 'new.db')]


def test_sqlite_replacement_revokes_native_store_admission(observed_route):
    import sqlite3
    with sqlite3.connect(observed_route.out / 'old.db') as db:
        db.execute('CREATE TABLE old_data (value TEXT)')
    done, receipt = observed_route.run('''import sqlite3
db = sqlite3.connect(out / "new.db")
db.close()
(out / "old.db").replace(out / "new.db")
with sqlite3.connect(out / "new.db") as db:
    db.execute("SELECT * FROM old_data").fetchall()''')
    assert done.returncode != 0
    assert 'SQLite store must be new' in str(receipt['violations'])


@pytest.mark.parametrize('suffix', ['-wal', '-shm', '-journal'])
def test_sqlite_preexisting_sidecar_refused(observed_route, suffix):
    (observed_route.out / ('new.db' + suffix)).write_bytes(b'old sidecar')
    done, receipt = observed_route.run('import sqlite3\nsqlite3.connect(out / "new.db")')
    assert done.returncode != 0
    assert 'SQLite store must be new' in str(receipt['violations'])


@pytest.mark.parametrize('with_teax', [False, True])
def test_declared_sources_are_the_route_the_tool_package_and_declared_teax(
        observed_route, monkeypatch, tmp_path, with_teax):
    """B8: permitted sources are stated by meaning, never by where read_coverage sits."""
    simkit = tmp_path / 'simkit-root'
    (simkit / 'simkit').mkdir(parents=True)
    (simkit / 'simkit' / '__init__.py').write_text('')
    if with_teax:
        monkeypatch.setenv('TEAX_SIMKIT_PATH', str(simkit))
    else:
        monkeypatch.delenv('TEAX_SIMKIT_PATH', raising=False)
    done, receipt = observed_route.run('(package_dir / "value.json").read_text()')
    assert done.returncode == 0, done.stderr
    sources = {Path(row['path']) for row in receipt['declarations']
               if row['category'] == 'declared-source'}
    tool_package = (roots.TOOL_HOME / 'sysml_codegen').resolve()
    permitted = [observed_route.route.resolve(), tool_package] + ([simkit.resolve()] if with_teax else [])
    assert all(any(path.is_relative_to(root) for root in permitted) for path in sources)
    assert tool_package / 'study' / 'read_coverage.py' in sources
    assert (simkit.resolve() / 'simkit' / '__init__.py' in sources) is with_teax


# ------------------------------------------------ the route's project root (B1, observed)


def _without_project_root():
    return {k: v for k, v in os.environ.items() if k != roots.PROJECT_ROOT_ENV}


def test_a_route_that_asks_for_its_project_root_gets_the_packages_work_tree(
        observed_route, tmp_path):
    """``run_route`` resolves the root before it observes, so the route never starts git.

    Before it did, a route run outside ``integrate`` with no ``SYSML_CODEGEN_PROJECT_ROOT``
    asked ``roots`` for the root under observation. ``roots`` ran git, and the observer refused
    git's output pipe as ``unsupported integer-descriptor open: 3``, which names no cause. The
    original tools found the root from ``__file__`` and never ran git.
    """
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    done, receipt = observed_route.run(
        'from sysml_codegen.study import roots\nreturn {"root": roots.project_root()}',
        env=_without_project_root(), cwd=tmp_path)
    assert done.returncode == 0, done.stderr
    assert receipt['violations'] == []
    assert coverage.valid_receipt(receipt, 'test-token')
    assert json.loads(done.stdout) == {'root': str(tmp_path.resolve())}


def test_a_package_in_no_work_tree_fails_closed_naming_the_cause(observed_route, tmp_path):
    """With no root to pin, no route runs, and the receipt says why in ``roots``' own words."""
    assert subprocess.run(['git', '-C', str(tmp_path), 'rev-parse'],
                          capture_output=True).returncode != 0, 'tmp_path must be in no work tree'
    done, receipt = observed_route.run('(out / "ran").write_text("the route ran")',
                                       env=_without_project_root())
    assert done.returncode != 0
    assert receipt['outcome'] == 'fail'
    assert receipt['route_error'].startswith(
        f'RootError: no project root: the package {observed_route.package} is in no git work tree')
    assert receipt['violations'] == [receipt['route_error']]
    assert receipt['reads'] == [] and receipt['declarations'] == []
    assert not (observed_route.out / 'ran').exists()
    assert not coverage.valid_receipt(receipt, 'test-token', allow_route_error=True)
