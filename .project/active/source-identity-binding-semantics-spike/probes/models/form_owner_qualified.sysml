package FormOwnerQualified {
    private import ScalarValues::*;

    // Spike probe fixture (SOURCE-IDENTITY Item 1) — owner-qualified form.
    // Identical topology to form_bare; only the binding RHS spelling differs:
    // the reference is qualified through the owning part def's name.
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
            // FORM UNDER TEST: owner-qualified RHS
            in R = 'Probe Plant'::R;
        }
        calc c2 : ThriceCalc {
            in R = 'Probe Plant'::R;
        }
    }

    part design_ctx {
        part plant : 'Probe Plant' {
            :>> R = 12.7;
        }
    }
}
