package AggLocalTermProbe {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;

    // =====================================================================
    // The aggregation LocalTerm mint (Item 2, obligation 1).
    //
    // `graph_builder.py`'s LocalTerm arm falls to its own entry-point mint only
    // when the referenced PartDef-local attribute is NEITHER a sibling
    // aggregation output NOR an EXPOSE alias. Every committed fixture missed
    // that: `solar_battery_model`'s five local terms are all one or the other
    // (`misc_hardware_cost` is an alias onto `allocation_model.total_allocation`;
    // `capital_cost`/`raw_material_cost` are sibling aggregation outputs), so
    // the mint had a population of zero and the D9 rule's third leg could not
    // be pinned live.
    //
    // `markup` here is the missing shape: a plain literal-valued attribute on the
    // aggregating part def, multiplied into the aggregation. It has no calc output
    // behind it, so it aliases to nothing and no sibling aggregation produces it.
    //
    // **Source**: authored fixture (CONSTRAINT-LIFECYCLE-REMEDIATION Item 2)
    // **Reference**: design.md R3/B4 third leg
    // =====================================================================

    calc def CellCostCalc {
        in attribute area : Real;
        out attribute cost : Real = area * 100.0;
    }

    part def 'Costed Thing' {
        attribute capital_cost : Real;
    }

    part def Cell :> 'Costed Thing' {
        attribute area : Real = 2.0;

        calc cost_model : CellCostCalc {
            in area = area;
        }

        :>> capital_cost = cost_model.cost;
    }

    part def Bank :> 'Costed Thing' {
        part cell : Cell[3];

        // The LocalTerm: a plain literal attribute, not a calc output and not a
        // sibling aggregation. This is what reaches the mint.
        attribute markup : Real = 1.15;

        :>> capital_cost = sum(cell.capital_cost) * markup;
    }

    part the_bank : Bank;
}
