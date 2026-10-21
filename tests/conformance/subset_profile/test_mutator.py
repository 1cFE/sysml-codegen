"""The mutation helpers do what they claim, on a module written for the purpose (design D5).

Each code shape the S1 spike met gets its own function in the sample module: a ``raise``, a
recorder call, ``return [finding]``, a raise in a nested function, a method using
zero-argument ``super()``, a raise of a helper's result (the hand-patch form), and a function
behind ``functools.lru_cache``, which must be refused. Every mutation is undone on exit, also
when the block raises. The last tests build, without applying, every mutation the licensed
tests apply, so a moved site or a renamed private name fails here, by name, first.

Pure: imports both packages but loads no model.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
import textwrap
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest

from tests.helpers.subset_profile import mutate, site_scan
from tests.helpers.subset_profile.mutate import MutationError, Rewrite, Target

SAMPLE = textwrap.dedent(
    """\
    from __future__ import annotations

    import functools


    class Refusal(Exception):
        pass


    def raises(x: object) -> str:
        if x:
            raise Refusal("raises")
        return "ok"


    class Recorder:
        def __init__(self) -> None:
            self.found: list[object] = []

        def record(self, x: object) -> list[object]:
            if x:
                self.found.append(x)
            return self.found


    def returns_list(x: object) -> list[object]:
        if x:
            return [x]
        return ["none"]


    class Base:
        def check(self, x: object) -> str:
            return "base"


    class Child(Base):
        def check(self, x: object) -> str:
            if x:
                raise Refusal("child")
            return super().check(x)


    def outer(x: object) -> str:
        def inner() -> str:
            if x:
                raise Refusal("inner")
            return "inner ok"

        return inner()


    def make(x: object) -> Refusal:
        return Refusal(str(x))


    def caller(x: object) -> str:
        if x:
            raise make(x)
        return "ok"


    @functools.lru_cache
    def cached(x: int) -> int:
        if x:
            raise Refusal("cached")
        return x


    def one_line(x: object) -> str:
        if x: raise Refusal("one line")  # noqa: E701
        return "ok"


    def assigns(x: object) -> object:
        y = x
        return y
    """
)


@pytest.fixture
def sample(tmp_path: Path) -> Iterator[ModuleType]:
    path = tmp_path / "mutator_sample.py"
    path.write_text(SAMPLE, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("mutator_sample", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    yield module
    del sys.modules[spec.name]


def _line(text: str) -> int:
    """The sample line holding ``text``."""
    (line,) = [i for i, row in enumerate(SAMPLE.splitlines(), 1) if text in row]
    return line


def _at(module: ModuleType, function: str, text: str) -> Target:
    return Target(module, function, _line(text))


def test_a_raise_becomes_pass_and_comes_back(sample: ModuleType) -> None:
    target = _at(sample, "raises", 'raise Refusal("raises")')
    original = sample.raises.__code__
    with mutate.rewritten(target, mutate.neutral(target)):
        assert sample.raises(True) == "ok"
    assert sample.raises.__code__ is original
    with pytest.raises(sample.Refusal):
        sample.raises(True)


def test_a_by_name_import_sees_the_change(sample: ModuleType) -> None:
    alias = sample.raises  # what `from module import raises` binds
    target = _at(sample, "raises", 'raise Refusal("raises")')
    with mutate.rewritten(target, mutate.neutral(target)):
        assert alias(True) == "ok"


def test_a_recorder_call_becomes_pass(sample: ModuleType) -> None:
    target = _at(sample, "Recorder.record", "self.found.append(x)")
    with mutate.rewritten(target, mutate.neutral(target)):
        assert sample.Recorder().record("finding") == []
    assert sample.Recorder().record("finding") == ["finding"]


def test_a_returned_finding_list_becomes_empty(sample: ModuleType) -> None:
    target = _at(sample, "returns_list", "return [x]")
    with mutate.rewritten(target, mutate.neutral(target)):
        assert sample.returns_list("finding") == []


def test_a_zero_argument_super_method_recompiles(sample: ModuleType) -> None:
    target = _at(sample, "Child.check", 'raise Refusal("child")')
    with mutate.rewritten(target, mutate.neutral(target)):
        assert sample.Child().check(True) == "base"


def test_a_nested_function_is_rewritten_through_its_outer_function(sample: ModuleType) -> None:
    target = _at(sample, "outer.inner", 'raise Refusal("inner")')
    original = sample.outer.__code__
    with mutate.rewritten(target, mutate.neutral(target)):
        assert sample.outer(True) == "inner ok"
    assert sample.outer.__code__ is original


def test_a_named_statement_is_rewritten_by_its_text(sample: ModuleType) -> None:
    target = _at(sample, "make", "return Refusal(str(x))")
    with mutate.rewritten(target, (Rewrite("caller", "raise make(x)", "pass"),)):
        assert sample.caller(True) == "ok"


def test_a_named_statement_that_is_not_there_is_refused(sample: ModuleType) -> None:
    target = _at(sample, "make", "return Refusal(str(x))")
    with pytest.raises(MutationError, match="0 statements"):
        with mutate.rewritten(target, (Rewrite("caller", "raise other(x)", "pass"),)):
            pass


def test_a_cached_function_is_refused(sample: ModuleType) -> None:
    target = _at(sample, "cached", 'raise Refusal("cached")')
    with pytest.raises(MutationError, match="caching wrapper"):
        with mutate.rewritten(target, mutate.neutral(target)):
            pass


def test_a_statement_with_no_neutral_form_is_refused(sample: ModuleType) -> None:
    with pytest.raises(MutationError, match="no neutral form for a Assign"):
        mutate.neutral(_at(sample, "assigns", "y = x"))


def test_the_code_comes_back_when_the_block_raises(sample: ModuleType) -> None:
    target = _at(sample, "raises", 'raise Refusal("raises")')
    original = sample.raises.__code__
    with pytest.raises(ZeroDivisionError):
        with mutate.rewritten(target, mutate.neutral(target)):
            _ = 1 / 0
    assert sample.raises.__code__ is original


def test_a_target_fires_only_when_its_statement_runs(sample: ModuleType) -> None:
    targets = {
        "raise": _at(sample, "raises", 'raise Refusal("raises")'),
        "inner": _at(sample, "outer.inner", 'raise Refusal("inner")'),
        "record": _at(sample, "Recorder.record", "self.found.append(x)"),
    }
    with mutate.recording_fired(targets) as fired:
        assert sample.raises(False) == "ok"
        with pytest.raises(sample.Refusal):
            sample.outer(True)
        sample.Recorder().record(None)
    assert fired == {"inner"}


def test_a_statement_sharing_its_line_cannot_be_recorded(sample: ModuleType) -> None:
    target = _at(sample, "one_line", 'raise Refusal("one line")')
    with pytest.raises(MutationError, match="shares its first line"):
        with mutate.recording_fired({"one_line": target}):
            pass


def test_a_package_init_site_imports_the_package_itself() -> None:
    """A site in ``pkg/__init__.py`` targets ``pkg``, the module its callers run.

    Importing ``pkg.__init__`` would load a second copy whose functions nothing calls, so a
    recorder or rewrite there would see nothing. No scanned site lives in a package
    ``__init__.py`` since the preflights moved to ``cli/prepare.py`` (Item 2b D1), so the
    mapping is checked on its own and a moved site on its new module.
    """
    assert mutate.module_name("sysml_codegen/cli/__init__.py") == "sysml_codegen.cli"
    assert mutate.module_name("sysml_codegen/elaboration/graph.py") == (
        "sysml_codegen.elaboration.graph"
    )
    target = mutate.site_target(
        "sysml_codegen/cli/prepare.py::_check_duplicate_output_paths::free-text::"
        "CodeGenerationError::1"
    )
    assert target.module is sys.modules["sysml_codegen.cli.prepare"]


# ---- the mutations the licensed tests apply ---------------------------------------------------


@pytest.mark.parametrize(("module", "dotted"), mutate.PATCHED_NAMES, ids=lambda v: str(v))
def test_every_patched_private_name_resolves(module: str, dotted: str) -> None:
    holder: object = importlib.import_module(module)
    for name in dotted.split("."):
        holder = getattr(holder, name)


def _mutated_sites() -> list[str]:
    shared_rule = [r.site_id for r in site_scan.load_account().rows if r.rules]
    return sorted(shared_rule) + sorted(mutate.SHARED)


@pytest.mark.parametrize("site_id", _mutated_sites(), ids=str)
def test_every_planned_site_mutation_builds(site_id: str) -> None:
    target = mutate.site_target(site_id)
    rewrites = mutate.HAND_PATCHES.get(site_id) or mutate.neutral(target)
    assert mutate._swaps(target, rewrites)
    with mutate.recording_fired({site_id: target}):
        pass


def test_every_hand_patch_is_a_planned_mutation() -> None:
    assert set(mutate.HAND_PATCHES) <= set(_mutated_sites())
