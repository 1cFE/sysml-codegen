package U5UsageQualNamedSibling {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — the author names ONE specific sibling usage (`comp_a`) while a
    // second occurrence of the same definition (`comp_b`) sits beside it. The written
    // reference is unambiguous to a reader. Does the route honour the named usage, refuse
    // as ambiguous, or pick one silently?
    calc def AreaCalculation {
        in attribute length_in : Real;
        out attribute area : Real = length_in * 2.0;
    }

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' { :>> length = 3.0; }
        part comp_b : 'Component' { :>> length = 7.0; }

        // The author means comp_a's 3.0.
        calc area_calc : AreaCalculation {
            in length_in = comp_a::length;
        }
    }

    part plant : 'Plant';
}
