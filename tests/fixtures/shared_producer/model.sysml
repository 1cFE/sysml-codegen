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
    // ⚠ HEADER CORRECTED (Gate B / Item 3, 2026-07-19). The paragraph here used to
    // claim both consumers converge positively on `SharedProducer__the_rig__gain`.
    // Live behavior: only the CONSTRAINT does. The calc reaches a terminal miss and
    // mints `SharedProducer__the_rig__scaler__gain`. See decision.md "Surfaced".
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
