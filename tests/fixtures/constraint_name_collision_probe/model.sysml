package ConstraintNameCollision {
    private import ScalarValues::*;

    // =====================================================================
    // R10 collision probe (recovery REVISE step 5).
    //
    // Two constraint usages that share ONE name under ONE part owner. The
    // constraint entry-point key is `{owner}__{usage}__{formal}`, so both
    // usages here would mint `ConstraintNameCollision__the_host__viability__threshold`.
    // The product must not let one key stand for two constraints.
    //
    // The control fixture `constraint_name_collision_control` is this file with
    // the second usage renamed to `backup_viability` and nothing else changed;
    // it is what proves the name is the whole cause.
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
        The single owner both same-named constraint usages sit under.

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

        // Same name, same owner, different actual. This is the collision.
        assert constraint viability : 'Viability Threshold' {
            in gain_in = backup_gain;
        }
    }
}
