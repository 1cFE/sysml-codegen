package FormControlRenamed {
    private import ScalarValues::*;

    // Spike probe fixture (SOURCE-IDENTITY Item 1) — CONTROL case.
    // Identical to form_bare except the calc parameter is named differently
    // from the attribute (`r_in` vs `R`), removing the shadowing collision.
    // Whatever `= R` resolves to here isolates the effect of the name clash.
    // Throwaway probe model; not part of the test corpus.

    calc def TwiceCalcRenamed {
        in attribute r_in : Real;
        out attribute y : Real = r_in * 2.0;
    }

    calc def ThriceCalcRenamed {
        in attribute r_in : Real;
        out attribute z : Real = r_in * 3.0;
    }

    part def 'Probe Plant' {
        attribute R : Real default 3.0;

        calc c1 : TwiceCalcRenamed {
            // CONTROL: bare RHS, no param/attribute name collision
            in r_in = R;
        }
        calc c2 : ThriceCalcRenamed {
            in r_in = R;
        }
    }

    part design_ctx {
        part plant : 'Probe Plant' {
            :>> R = 12.7;
        }
    }
}
