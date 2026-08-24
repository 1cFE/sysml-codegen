package FormBracketHash {
    private import ScalarValues::*;

    // Spike probe fixture (SOURCE-IDENTITY Item 1) — bracketed occurrence-index
    // form, KerML index-operator spelling `#(i)`. Whether `plants#(1).R` parses,
    // and what it denotes if it does, is the probe question.
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
        attribute R : Real = 3.0;
    }

    part def 'Design Ctx' {
        part plants : 'Probe Plant'[2];

        calc c1 : TwiceCalc {
            // FORM UNDER TEST: KerML index-operator RHS
            in R = plants#(1).R;
        }
        calc c2 : ThriceCalc {
            in R = plants#(2).R;
        }
    }

    part design_ctx : 'Design Ctx';
}
