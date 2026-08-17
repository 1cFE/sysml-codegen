package S6QualSiblingScope {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — owner-qualified reference whose qualifying definition has NO
    // occurrence in the consumer's own containment, but exactly one occurrence under a
    // SIBLING subtree. Does the exact route reach sideways, silently?
    calc def UnitCost {
        in attribute unit_cost : Real;
        out attribute total_cost : Real = unit_cost * 2.0;
    }

    part def 'Unit' {
        attribute cost : Real default 5.0;
    }

    part def 'Balance Of Plant' {
        part the_unit : 'Unit' {
            :>> cost = 7.0;
        }
    }

    part def 'Power Block' {
        // No 'Unit' occurrence anywhere under this part.
        calc cost_calc : UnitCost {
            in unit_cost = 'Unit'::cost;
        }
    }

    part def 'Plant' {
        part bop : 'Balance Of Plant';
        part block : 'Power Block';
    }

    part plant : 'Plant';
}
