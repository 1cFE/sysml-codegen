# constraint_blocked_profile

Authored by the CONSTRAINT-EXEC orchestrator (2026-07-12) as the Item 5 audit's
cure for its note 3: a fixture whose single assertion uses real-valued equality
(profile-blocked, `block_real_equality`), proving the preflight halt fires
through the WIRED pipeline path (`build_pipeline_context(...,
lower_constraints_enabled=True)`), not only via direct `lower_constraints` calls.
Derived from `constraint_inline`'s layout.
