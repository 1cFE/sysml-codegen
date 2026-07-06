package TwoLevelLib {
    private import ScalarValues::*;

    // Nested cost calc inside the driver. Its output `gamma` is the head of the
    // gamma -> lcoe edge (SC-2), identical to spec_chain_channel's MeierCost.
    calc def MeierCost {
        in attribute drive_power : Real;
        out attribute gamma : Real = drive_power * 0.02;
    }

    // Plant-level consumer calc (the lcoe analog). Binds cost_per_joule from the
    // driver. In THIS fixture the consumer is declared on the BASE plant def.
    calc def LcoeCalc {
        in attribute cost_per_joule : Real;
        out attribute lcoe : Real = cost_per_joule * 100.0;
    }

    // Base driver: declares cost_per_joule WITHOUT a value (base def tier).
    part def 'IFE Driver' {
        attribute drive_power : Real = 50.0;
        attribute cost_per_joule : Real;

        calc meier_cost : MeierCost {
            in drive_power = drive_power;
        }
    }

    // Specialized driver: bare `:>> cost_per_joule = meier_cost.gamma` (value-carrying
    // redefinition, ReferenceUsage — captured by hierarchy extraction). This is the
    // exact shape of fusion-tea hif_driver.sysml:82 (D-F bare form).
    part def 'HIF Driver' :> 'IFE Driver' {
        :>> cost_per_joule = meier_cost.gamma;
    }

    // BASE plant def: owns BOTH the base-typed `driver` AND the cross-part consumer
    // `lcoe_calc`. The consumer's DECLARING def is this base — mirroring fusion-tea's
    // 'IFE Power Plant' (designs/generic_ife/ife_plant.sysml), which declares lcoe_calc
    // and `part driver : 'IFE Driver'`. There is NO 'HIF Plant' def: the two-level shape
    // is a part USAGE typed by this base with an inline `:>> driver` retype (see design).
    part def 'IFE Power Plant' {
        part driver : 'IFE Driver';

        calc lcoe_calc : LcoeCalc {
            in cost_per_joule = driver.cost_per_joule;
        }
    }
}
