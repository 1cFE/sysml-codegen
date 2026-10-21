"""No covered refusal site is reachable after the first write (Item 2b D14, spec Criterion 3).

``emit_package`` is the only code that writes under the destination. A name-based call
closure from it over ``src/sysml_codegen/`` (``site_scan.call_closure``) is joined with the
site account: no site whose role is ``public_capability``, ``malformed_input``, ``unknown`` or
``relay_plumbing`` may sit in a function the closure reaches, except the sites allowed below
by name, each with its reason.

Stated limit: the closure is name-based and follows neither a call made through ``getattr``
nor a callable stored and called under another name. It over-approximates every other call
(a bare name reaches every function of that name), so a site it misses would have to be
reached through one of those two forms.
"""

from __future__ import annotations

from tests.helpers.refusal_cases import site_scan
from tests.helpers.refusal_cases.site_scan import Role

COVERED = frozenset(
    {Role.PUBLIC_CAPABILITY, Role.MALFORMED_INPUT, Role.UNKNOWN, Role.RELAY_PLUMBING}
)

CONSTRAINT_GRAPH_CHECK = (
    "sysml_codegen/generation/errors.py::validate_constraint_graph_or_raise::unrecognized::"
    "constraint_name_safety_error::1"
)
INTERNAL_DEFECT_RELAY = (
    "sysml_codegen/elaboration/elaborate.py::unexpected_public_failure::coded::SI_INTERNAL_DEFECT::1"
)
ALLOWED = {
    # Site 338. It stays inside generate_pipeline_yaml, generate_registry and
    # build_model_contract as their own guard, pinned by test_module_kind_faildloud.py. It
    # cannot fire after the first write: prepare's constraint-names step runs the same check
    # on the same Prepared.graph first (test below).
    CONSTRAINT_GRAPH_CHECK: "prepare's constraint-names step already ran it on the same graph",
    # The factory that wraps an unclassified exception as SI_INTERNAL_DEFECT. emit_package
    # calls it for a writer failure nobody classified (design D18). It owns no refusal: what
    # it wraps after the first write is raised at a site this test keeps unreachable, or at
    # an internal_invariant or environment site.
    INTERNAL_DEFECT_RELAY: "relay for writer failures (D18); originating sites own the refusal",
}

EMIT_PACKAGE = ("sysml_codegen/cli/emit.py", "emit_package")


def _covered_sites_reached_from(root: site_scan.FunctionKey) -> set[str]:
    reach = site_scan.call_closure([root])
    sites = site_scan.scan().by_id()
    return {
        row.site_id
        for row in site_scan.load_account().rows
        if row.role in COVERED
        and (sites[row.site_id].file, sites[row.site_id].function) in reach
    }


def test_no_covered_site_is_reachable_from_emit_package():
    assert _covered_sites_reached_from(EMIT_PACKAGE) == set(ALLOWED)


def test_the_constraint_names_step_runs_the_allowed_check():
    """The allowance for site 338 lasts only while prepare runs the same check first."""
    preflight = ("sysml_codegen/cli/prepare.py", "_preflight_constraint_names")
    assert preflight in site_scan.call_closure([("sysml_codegen/cli/prepare.py", "prepare_graph")])
    assert ("sysml_codegen/generation/errors.py", "validate_constraint_graph_or_raise") in (
        site_scan.call_closure([preflight])
    )


def test_the_writers_no_longer_run_the_preflights():
    """D14 dropped the writers' own re-checks; prepare's steps are not reachable from emit."""
    reach = site_scan.call_closure([EMIT_PACKAGE])
    for name in (
        "_preflight_constraint_names",
        "_preflight_generation_metadata",
        "_preflight_exit_point_types",
        "_preflight_registry_class_names",
        "_preflight_constraint_totality",
        "_preflight_coverage_account",
    ):
        assert ("sysml_codegen/cli/prepare.py", name) not in reach, name
    assert ("sysml_codegen/generation/entry_point.py", "_refuse_colliding_field_names") not in reach
