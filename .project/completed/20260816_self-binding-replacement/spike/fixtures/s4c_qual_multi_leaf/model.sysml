package S4CQualMultiLeaf {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — shape 4 (D-6), owner-qualified reference authored INSIDE the
    // part definition, qualifying a CHILD definition that has TWO leaf occurrences in
    // the consumer's own context. This is the [HARD] SI_OCCURRENCE_AMBIGUOUS case.
    calc def UnitCost {
        in attribute unit_cost : Real;
        out attribute total_cost : Real = unit_cost * 2.0;
    }

    part def 'Unit' {
        attribute cost : Real default 5.0;
    }

    part def 'Plant' {
        part unit_a : 'Unit' {
            :>> cost = 3.0;
        }
        part unit_b : 'Unit' {
            :>> cost = 7.0;
        }

        calc cost_calc : UnitCost {
            in unit_cost = 'Unit'::cost;
        }
    }

    part plant : 'Plant';
}
