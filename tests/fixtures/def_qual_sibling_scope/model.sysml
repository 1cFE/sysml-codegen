package def_qual_sibling_scope {
    private import ScalarValues::*;

    // D-6, definition-owned leaf: the qualifying definition has NO occurrence
    // in the consumer's own containment, but exactly one occurrence under a
    // SIBLING subtree. Expected: generates — the positional fallback searches
    // descendants of each lineage anchor and selects the single sibling
    // occurrence, silently crossing a containment boundary the author never
    // named (spike F-4). This is fallback behavior, not checked author intent.
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
