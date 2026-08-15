package ConstraintNameCollision {
    private import ScalarValues::*;

    // =====================================================================
    // R10 control (recovery REVISE step 5).
    //
    // `constraint_name_collision_probe` with the second constraint usage
    // renamed `viability` -> `backup_viability`, and nothing else changed.
    // The test strips comments and applies the reverse rename to prove that
    // the name is the sole difference, so whatever the two fixtures do
    // differently is caused by the name and by nothing else.
    //
    // This is the side that shows what a non-colliding pair mints: two
    // distinct `...__threshold` keys under one owner.
    //
    // **Source**: authored fixture (cutover-recovery REVISE step 5, R10)
    // **Reference**: .project/active/cutover-recovery/owner-disposition-20260811.md step 4
    // **Last Updated**: 2026-08-11
    //
    // Not a corpus fixture: it carries no `extraction_snapshot.json`, so
    // `scripts/run_elaboration_corpus.py` never discovers it, and it joins no
    // ledger row.
    // =====================================================================

    constraint def 'Viability Threshold' {
        doc /*
        Gate A's constraint shape: one bound actual, one defaulted formal.

        **Source**: `tests/fixtures/gate_a_d5/model.sysml`
        **Reference**: tests/fixtures/gate_a_d5/PROVENANCE.md
        **Last Updated**: 2026-08-11
        */

        in attribute gain_in : Real;
        in attribute threshold : Real default 10.0;

        gain_in >= threshold
    }

    calc def Doubler {
        doc /*
        Unrelated calculation. The route refuses a model with no calc
        definition at all, so the fixture carries one that neither produces
        nor consumes either constrained attribute.

        **Source**: authored fixture (cutover-recovery REVISE step 5, R10)
        **Reference**: tests/fixtures/gate_a_d5/model.sysml
        **Last Updated**: 2026-08-11
        */

        in attribute seed_in : Real;
        out attribute doubled : Real = seed_in * 2.0;
    }

    part def Unrelated {
        doc /*
        Carrier for the unrelated calculation.

        **Source**: authored fixture (cutover-recovery REVISE step 5, R10)
        **Reference**: tests/fixtures/gate_a_d5/model.sysml
        **Last Updated**: 2026-08-11
        */

        attribute seed : Real = 3.0;

        calc doubler : Doubler {
            in seed_in = seed;
        }
    }

    part the_other : Unrelated;

    part def Host {
        doc /*
        The single owner both constraint usages sit under.

        **Source**: authored fixture (cutover-recovery REVISE step 5, R10)
        **Reference**: .project/active/cutover-recovery/plan.md
        **Last Updated**: 2026-08-11
        */
    }

    part the_host : Host {
        attribute primary_gain : Real = 40.0;
        attribute backup_gain : Real = 20.0;

        assert constraint viability : 'Viability Threshold' {
            in gain_in = primary_gain;
        }

        // Distinct name, same owner, same actual as the probe's second usage.
        assert constraint backup_viability : 'Viability Threshold' {
            in gain_in = backup_gain;
        }
    }
}
