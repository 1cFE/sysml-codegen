package FormBare {
    private import ScalarValues::*;

    // Spike probe fixture (SOURCE-IDENTITY Item 1) — bare self-named form.
    // Customer shape: attribute + two self-named calc consumers in the same
    // part def scope, literal :>> override at a concrete occurrence.
    // Throwaway probe model; not part of the test corpus.

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

        calc c1 : TwiceCalc {
            // FORM UNDER TEST: bare self-named RHS
            in R = R;
        }
        calc c2 : ThriceCalc {
            in R = R;
        }
    }

    part design_ctx {
        part plant : 'Probe Plant' {
            :>> R = 12.7;
        }
    }
}
