package GateAPackageOwner {
    private import ScalarValues::*;

    // =====================================================================
    // The genuinely package-owned constraint control (Item 2, design M6).
    //
    // No fixture in the repo declares a constraint directly in a package body
    // today, so the surviving `package` owner branch of
    // `prepare_constraint_usages` has zero live coverage. This fixture is that
    // coverage: the constraint's immediate owner IS the package, so
    // `owner.owner` and `owner.owning_definition` name the same element and
    // the new `part_usage` branch must not claim it.
    //
    // **Source**: authored fixture (CONSTRAINT-LIFECYCLE-REMEDIATION Item 2)
    // **Reference**: design.md Phase 0 / Phase 2 validation
    // =====================================================================

    constraint def 'Package Threshold' {
        in attribute limit : Real;
        in attribute floor : Real default 1.0;

        limit >= floor
    }

    // Carried for the same reason as gate_a's: the pipeline refuses a model with
    // no calc definition. Unrelated to `limit`.
    calc def Doubler {
        in attribute seed : Real;
        out attribute doubled : Real = seed * 2.0;
    }

    part def Unrelated {
        attribute seed : Real = 3.0;

        calc doubler : Doubler {
            in seed = seed;
        }
    }

    part the_other : Unrelated;

    attribute limit : Real = 5.0;

    assert constraint pkg_check : 'Package Threshold' {
        in limit = limit;
    }
}
