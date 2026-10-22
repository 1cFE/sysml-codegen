"""The scanner sees a new refusal site, or names it as unrecognized (Item 2a E2).

Each snippet is written as a module of a synthetic ``sysml_codegen`` tree and scanned with the
real agentic-mbse source beside it, as the account's scan is. A snippet passes when the site it
adds appears with the channel and code the scanner's forms give it. A raise outside those forms
must still appear, as ``unrecognized`` and named by what it raises, so nothing raised under
``src/sysml_codegen/`` is invisible to the account.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from tests.helpers.refusal_cases import site_scan

#: (snippet, the site's function, channel, code)
NEW_RAISE_PER_FORM = [
    (
        "def f():\n    raise ElaborationInvariantError(ElaborationCode.SI_NEW, 'd')\n",
        "f",
        "coded",
        "SI_NEW",
    ),
    (
        "class NewFixedError(ElaborationInvariantError):\n"
        "    def __init__(self):\n"
        "        super().__init__(ElaborationCode.SI_FIXED, 'd')\n"
        "def f():\n    raise NewFixedError()\n",
        "f",
        "coded-fixed",
        "SI_FIXED",
    ),
    (
        "def f(error):\n    return Diagnostic(code=error.code, consumer=None)\n",
        "f",
        "coded-relay",
        "error.code",
    ),
    (
        "def pick():\n    return ElaborationCode.SI_PICKED\n"
        "def f():\n    code = pick()\n    return Diagnostic(code=code, consumer=None)\n",
        "f",
        "coded-returned",
        "SI_PICKED",
    ),
    (
        "TABLE = {1: ElaborationCode.SI_ONE}\n"
        "def f(k):\n"
        "    return Diagnostic(code=TABLE.get(k, ElaborationCode.SI_TWO), consumer=None)\n",
        "f",
        "coded-mapped",
        "SI_ONE|SI_TWO",
    ),
    (
        "def novel_factory(code, detail):\n    return ReadinessFinding(code, detail)\n",
        "novel_factory",
        "plumbing",
        "code",
    ),
    ("def f():\n    raise SysMLParsingError('d')\n", "f", "free-text", "SysMLParsingError"),
    ("def f():\n    raise KeyError('d')\n", "f", "builtin", "KeyError"),
]
NEW_EXCEPTION_CLASS = (
    "class NovelError(Exception):\n    pass\ndef f():\n    raise NovelError('d')\n",
    "f",
    site_scan.UNRECOGNIZED,
    "NovelError",
)
NEW_RAISING_HELPER = (
    "def _novel_refusal():\n    return NovelError('d')\ndef f():\n    raise _novel_refusal()\n",
    "f",
    site_scan.UNRECOGNIZED,
    "_novel_refusal",
)
COMPUTED_CODE_MAP = (
    "def f(kind):\n    return Diagnostic(code=code_for(kind), consumer=None)\n",
    "f",
    "coded-DYNAMIC",
    "code_for(kind)",
)


def _scan_snippet(snippet: str, tmp_path: Path) -> list[site_scan.Site]:
    package = tmp_path / "sysml_codegen"
    package.mkdir()
    (package / "synthetic.py").write_text(textwrap.dedent(snippet))
    return [
        s
        for s in site_scan.scan(codegen_src=tmp_path).sites
        if s.file == "sysml_codegen/synthetic.py"
    ]


@pytest.mark.parametrize(
    ("snippet", "function", "channel", "code"),
    [*NEW_RAISE_PER_FORM, NEW_EXCEPTION_CLASS, NEW_RAISING_HELPER, COMPUTED_CODE_MAP],
    ids=[
        *(f"new_{form[2]}" for form in NEW_RAISE_PER_FORM),
        "new_exception_class",
        "new_raising_helper",
        "computed_code_map",
    ],
)
def test_synthetic_site_detected_or_reported_unrecognized(
    snippet, function, channel, code, tmp_path
):
    found = {(s.function, s.channel, s.code) for s in _scan_snippet(snippet, tmp_path)}
    assert (function, channel, code) in found


def test_a_raise_of_a_recognized_construction_is_not_also_unrecognized(tmp_path):
    sites = _scan_snippet(
        "def f():\n"
        "    raise ElaborationDiagnosticError((Diagnostic(code=ElaborationCode.SI_X),))\n",
        tmp_path,
    )
    assert [(s.channel, s.code) for s in sites] == [("coded", "SI_X")]


def test_a_bare_reraise_is_unrecognized_by_name(tmp_path):
    sites = _scan_snippet(
        "def f():\n    try:\n        g()\n    except KeyError:\n        raise\n", tmp_path
    )
    assert [(s.channel, s.code) for s in sites] == [(site_scan.UNRECOGNIZED, "<reraise>")]
