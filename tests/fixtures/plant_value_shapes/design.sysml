package PlantValueShapesDesign {
    private import ScalarValues::*;
    private import PlantValueShapesLib::*;

    part shapes_design {

        // --- Shape 1: attribute-def-typed attr with nested `:>>`, fed to a calc.
        attribute availability : 'Econ Param' {
            doc /* Nested `:>>` sets the bundled sub-attributes (14-econ-params shape). */
            :>> value = 0.70;
            :>> min_value = 0.50;
            :>> max_value = 1.00;
        }

        // --- Shape 2: bare `default 10.0` (no `:=`).
        attribute rate_default : Real default 10.0;

        // --- Shape 3: doc bodies inside a calc usage and on a `:>>` redefinition.
        calc rated_cost : RatedCostCalc {
            doc /* Doc body inside a calc usage (shape 3). */
            in rate = availability.value;
        }

        calc net_cost_calc : NetCostCalc {
            in revenue = 200.0;
        }

        calc mixed_style : 'Mixed Output Style' {
            in base = 4.0;
        }

        calc quoted_return : 'Quoted Return Calc' {
            in amount = 6.0;
        }

        // --- Shape 4: consume 'Flow Sub' — the in-binding references an inherited
        // attr the same def redefines below it.
        part flow_unit : 'Flow Sub';

        // --- Shape 5: instantiate a mid-chain concrete member of the 5-deep chain.
        part chain_unit : 'Chain L4';

        // --- Shapes 6 + 9: usage-level quoted enum `:>>` and the non-float EP.
        // The chamber's enum-valued `wall` is redefined to a quoted enum literal and
        // feeds the calc input one hop away (the `wall_type` idiom, Item 5 substrate).
        part chamber_unit : 'Chamber Unit' {
            :>> wall = 'Wall Kind'::liquid_wall {
                doc /* Doc body on a `:>>` redefinition (shape 3). */
            }
        }
    }
}
