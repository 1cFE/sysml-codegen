package SpecChainLib {
    private import ScalarValues::*;

    // Nested cost calc that lives inside the driver. Its output `gamma` is the
    // channel the specialized driver rebinds `cost_per_joule` to — the head of the
    // gamma -> lcoe edge (SC-2).
    calc def MeierCost {
        doc /*
        Nested producer calc for the gamma -> lcoe analog (SC-2). `gamma` is the
        specialized-nested-part calc OUTPUT that a cross-part consumer must reach
        through the redefinition chain (usage override > specialized-def :>> > base).
        **Source**: authored fixture (Item 10, UPSTREAM-FINDINGS stage (b))
        **Reference**: spec.md SC-2 (def/specialization channel idiom)
        **Last Updated**: 2026-07-05
        */
        in attribute drive_power : Real;
        out attribute gamma : Real = drive_power * 0.02;
    }

    // Plant-level consumer calc (the lcoe analog). It binds cost_per_joule from the
    // driver; after the Phase-7 resolver that source resolves to meier_cost.gamma.
    calc def LcoeCalc {
        in attribute cost_per_joule : Real;
        out attribute lcoe : Real = cost_per_joule * 100.0;
    }

    // Base driver: declares cost_per_joule WITHOUT a value (base def tier). No
    // channel wires it at this tier.
    part def 'IFE Driver' {
        attribute drive_power : Real = 50.0;
        attribute cost_per_joule : Real;

        calc meier_cost : MeierCost {
            in drive_power = drive_power;
        }
    }

    // Specialized driver: redefines cost_per_joule to bind the nested calc OUTPUT
    // (meier_cost.gamma). This is the specialized-def :>> tier the resolver follows.
    // Bare `:>> name = value` (the value-carrying redefinition idiom, like ife_plant
    // shape 2) — parses as a ReferenceUsage so hierarchy extraction captures it.
    part def 'HIF Driver' :> 'IFE Driver' {
        :>> cost_per_joule = meier_cost.gamma;
    }

    // Facility base: owns the driver typed to the base 'IFE Driver'.
    part def Facility {
        part driver : 'IFE Driver';
    }

    // Retyped variant: driver is redefined to the specialized 'HIF Driver' (so
    // cost_per_joule carries the specialized-def :>> binding to meier_cost.gamma).
    // The cross-part lcoe consumer lives here, on the instantiated def, so it binds
    // cost_per_joule from the RETYPED driver -> the consumer edge the resolver supplies.
    part def Variant :> Facility {
        part :>> driver : 'HIF Driver';

        calc lcoe_calc : LcoeCalc {
            in cost_per_joule = driver.cost_per_joule;
        }
    }
}
