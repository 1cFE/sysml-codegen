package PlantValueShapesLib {
    private import ScalarValues::*;

    // =====================================================================
    // Secondary fusion-tea syntactic shapes (Decision D4). Each shape's current
    // behavior — correct, degraded, or diagnostic — is measured at capture and
    // pinned as a specific observed property (SC-3), never a byte-equality. Any
    // shape that CRASHES the extractor (not merely degrades) is removed under the
    // L2-2 escape hatch and filed to the fixture-gap register with crash evidence.
    //
    // **Source**: authored fixture (PIPELINE-TRUTH Item 1), shaped after fusion-tea
    //   library/foundation/economic_parameter.sysml, library/cost_structure/ife_cost_parameters.sysml,
    //   designs/generic_ife/ife_subsystems.sysml
    // **Reference**: spec.md "Secondary shapes (the high-value subset — Decision D4)"
    // **Last Updated**: 2026-07-06
    // =====================================================================

    // --- Shape 1: attribute-def-typed attribute with nested `:>>` (14-econ-params
    // shape, fusion-tea 'Economic Parameter'). The attribute def bundles sub-attrs
    // that a usage sets via nested `:>>`.
    attribute def 'Econ Param' {
        attribute value : Real;
        attribute min_value : Real;
        attribute max_value : Real;
    }

    // --- Shape 6: quoted enum def (usage-level quoted `:>>` lives in design.sysml).
    enum def 'Wall Kind' {
        dry_wall;
        wetted_wall;
        liquid_wall;
    }

    // --- Shape 7: a quoted OUTPUT parameter name (`out attribute 'net cost'`).
    calc def NetCostCalc {
        in attribute revenue : Real;
        out attribute 'net cost' : Real = revenue * 0.5;
    }

    // --- Shape 8: Style-E — a quoted calc def mixing `out attribute` and `return`.
    calc def 'Mixed Output Style' {
        in attribute base : Real;
        out attribute doubled : Real = base * 2.0;
        return tripled : Real = base * 3.0;
    }

    // --- Shape 8b: a return inside a quoted calc def (return-in-quoted-def row).
    calc def 'Quoted Return Calc' {
        in attribute amount : Real;
        return scaled : Real = amount * 1.5;
    }

    // Plain calc consuming an econ-param sub-attribute (so shape 1 flows to a calc).
    calc def RatedCostCalc {
        in attribute rate : Real;
        out attribute cost : Real = rate * 100.0;
    }

    // --- Shape 5: a 5-deep specialization chain with abstract ends. L1 and L5
    // are abstract; L2..L4 concrete. Exercises deep supertype-chain resolution.
    abstract part def 'Chain L1' {
        attribute depth_marker : Real = 1.0;
    }
    part def 'Chain L2' :> 'Chain L1';
    part def 'Chain L3' :> 'Chain L2';
    part def 'Chain L4' :> 'Chain L3';
    abstract part def 'Chain L5' :> 'Chain L4';

    // --- Shape 4: an in-binding referencing an inherited attr the same def
    // redefines BELOW the binding. Base declares `throughput`; the subtype's calc
    // binds `in flow = throughput` and then redefines `:>> throughput` further down.
    part def 'Flow Base' {
        attribute throughput : Real;
    }

    calc def FlowCalc {
        in attribute flow_rate : Real;
        out attribute total : Real = flow_rate * 10.0;
    }

    part def 'Flow Sub' :> 'Flow Base' {
        calc flow_calc : FlowCalc {
            in flow_rate = throughput;      // references inherited attr...
        }
        :>> throughput = 8.0;          // ...which the same def redefines below.
    }

    // --- Shape 9: non-float entry-point shape — an enum-valued attribute one hop
    // from an entry point (the `wall_type` idiom). Item 5 substrate: its current
    // behavior (silent None-omission of the non-float EP) is pinned as observed.
    calc def ChamberSelectCalc {
        in attribute wall : 'Wall Kind';
        in attribute footprint : Real;
        out attribute rating : Real = footprint * 2.0;
    }

    // Hosts the enum-typed attribute so the design can redefine it via a usage-level
    // quoted enum `:>>` (shape 6) and feed it one hop to the calc input (shape 9).
    part def 'Chamber Unit' {
        attribute wall : 'Wall Kind';
        attribute footprint : Real = 12.0;

        calc select : ChamberSelectCalc {
            in wall = wall;
            in footprint = footprint;
        }
    }
}
