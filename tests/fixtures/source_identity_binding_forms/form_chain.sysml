package FormChain {
    private import ScalarValues::*;

    // Spike probe fixture (SOURCE-IDENTITY Item 1) — feature-chain form.
    // Same modeled meaning (one plant attribute R feeding two calcs), but the
    // consumers sit beside the part usage and reach the attribute through a
    // dotted feature chain. Throwaway probe model; not part of the test corpus.

    calc def TwiceCalc {
        in attribute R : Real;
        out attribute y : Real = R * 2.0;
    }

    calc def ThriceCalc {
        in attribute R : Real;
        out attribute z : Real = R * 3.0;
    }

    part def 'Probe Plant' {
        attribute R : Real default 3.0;
    }

    part def 'Design Ctx' {
        part plant : 'Probe Plant' {
            :>> R = 12.7;
        }

        calc c1 : TwiceCalc {
            // FORM UNDER TEST: feature-chain RHS
            in R = plant.R;
        }
        calc c2 : ThriceCalc {
            in R = plant.R;
        }
    }

    part design_ctx : 'Design Ctx';
}
