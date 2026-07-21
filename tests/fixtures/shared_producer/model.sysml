package SharedProducer {
    private import ScalarValues::*;

    // =====================================================================
    // Two-consumer convergence (Item 2, SR-A02 / SR-R23 / invariant I9).
    //
    // One usage-owned design attribute, `gain`, read by BOTH a calculation input
    // and a constraint actual. Contract invariant 21 requires them to converge on
    // the SAME QN-keyed typed entry point — one modeled default, one group
    // assignment — not two per-consumer mints.
    //
    // CLOSED by Item 4 (DD-R28, DD-A14). Both consumers now converge positively on
    // `SharedProducer__the_rig__gain` via row 16, the calc side reaching it through
    // the written-reference carry. The earlier note here — that only the CONSTRAINT
    // converged and the calc minted `SharedProducer__the_rig__scaler__gain` — was
    // correct for the Item 2/3 state and no longer describes this model.
    // See PROVENANCE.md and tests/conformance/test_shared_producer_convergence.py.
    //
    // `gate_a` deliberately has no calculation consumer, so it cannot carry this
    // row; this fixture is the shape SR-A02 needs.
    //
    // **Source**: authored fixture (CONSTRAINT-LIFECYCLE-REMEDIATION Item 2)
    // **Reference**: spec.md SR-A02, design.md I9
    // =====================================================================

    constraint def 'Gain Floor' {
        in attribute gain : Real;
        in attribute floor : Real default 10.0;

        gain >= floor
    }

    calc def Scaler {
        in attribute gain : Real;
        out attribute scaled : Real = gain * 2.0;
    }

    part def Rig;

    part the_rig : Rig {
        attribute gain : Real = 40.0;

        // Consumer 1: a calculation input.
        calc scaler : Scaler {
            in gain = gain;
        }

        // Consumer 2: a constraint actual, self-named, on the same attribute.
        assert constraint floor_check : 'Gain Floor' {
            in gain = gain;
        }
    }
}
