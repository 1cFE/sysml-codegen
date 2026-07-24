package GateBCollision {
    private import ScalarValues::*;

    // =====================================================================
    // Gate B probe 3 — an ATTEMPT to force the only shape that could make
    // extension-time V11 non-vacuous (probe 1 shape B, reached for real).
    //
    // Probe 1 proved: extension raises a genuinely-new V11 violation only when
    // an appended constraint module carries an entry_point input whose
    // qualified_name is already in `fallback_entry_points`.
    //
    // A fallback key is minted ONLY by the lenient calculation consumer as
    // `{calc_module_eqn}__{formal}` (dependency_backtracker.py:603 ->
    // producer_resolution.py:474). A constraint's DESIGN_ATTRIBUTE input
    // carries a design-attribute QN. So the collision needs a design
    // attribute whose QN is literally `{calc_module_eqn}__{formal}`.
    //
    // Attempt: put a calc usage `the_rig` and a part usage `the_rig` in the
    // SAME package namespace. The calc usage's unbound formal `gain` mints
    // fallback key `GateBCollision__the_rig__gain`; the part usage's own
    // attribute `gain` has design-attribute QN `GateBCollision__the_rig__gain`.
    // Same string. A self-named constraint actual on `the_rig` then makes the
    // appended constraint module wire that exact key.
    //
    // NOT a test fixture. Probe scratch; lives with the work item.
    // =====================================================================

    constraint def 'Nonneg' {
        in attribute v : Real;

        v >= 0.0
    }

    calc def Scaler {
        in attribute gain : Real;
        out attribute scaled : Real = gain * 2.0;
    }

    part def Rig;

    // (1) package-level calc usage named `the_rig`. `gain` is left UNBOUND, so
    //     it falls through and mints `GateBCollision__the_rig__gain`.
    calc the_rig : Scaler;

    // (2) package-level part usage with the SAME local name, carrying an
    //     attribute named `gain` -> QN `GateBCollision__the_rig__gain`.
    part the_rig : Rig {
        attribute gain : Real = 7.0;

        assert constraint nonneg : 'Nonneg' {
            in v = gain;
        }
    }
}
