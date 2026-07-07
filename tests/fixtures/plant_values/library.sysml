package PlantValuesLib {
    private import ScalarValues::*;

    // =====================================================================
    // Plant-level consumer calc + viability constraint (calc/constraint defs
    // belong in the library — ADR-002). The plant calc binds each input to a
    // SUBSYSTEM attribute cross-part; that cross-part reference is the shape
    // whose value the current pipeline cannot wire, so the entry point stays
    // valueless and V11 trips (the "before" state Item 2 flips).
    //
    // **Source**: authored fixture (PIPELINE-TRUTH Item 1), shaped after
    //   fusion-tea designs/generic_ife/ife_plant.sysml + designs/hif_ife/{hif_plant,hif_driver}.sysml
    // **Reference**: spec.md "The headline fixture" (mechanisms a/b/c)
    // **Last Updated**: 2026-07-06
    // =====================================================================

    // Plant cost calc — the lcoe_calc analog. Each `in` reads a subsystem attr
    // cross-part (mechanisms a/b/c). A representative closed form; the modeling
    // shape (cross-part inputs into one plant calc) is the point, not economics.
    calc def PlantCostCalc {
        in attribute driver_efficiency : Real;   // (a) subtype-def literal via retype
        in attribute target_cost : Real;         // (b) bare no-retype override block literal
        in attribute chamber_cost : Real;        // (c) plain cross-part attribute chain
        out attribute plant_cost : Real =
            (target_cost + chamber_cost) / driver_efficiency;
    }

    // eta*gain viability constraint (copied from fusion-tea fusion_cycle.sysml:29).
    // Carries a defaulted param (`threshold`) so the plant's assert usage can leave
    // it unbound — one of the three binding sub-shapes the assert constraint carries.
    constraint def 'Viability Threshold' {
        in attribute eta : Real;
        in attribute gain : Real;
        in attribute threshold : Real default 10.0;

        eta * gain >= threshold
    }

    // =====================================================================
    // Subsystem part defs. Base-tier attributes are declared WITHOUT values;
    // the plant USAGE (design.sysml) supplies them through mechanisms a/b/c.
    // =====================================================================

    // Mechanism (a): base driver declares `efficiency` valueless; a subtype def
    // sets it via a literal `:>>` on the DEF; the plant usage retypes the driver
    // part to the subtype (usage-level retype). Copied from fusion-tea 'IFE
    // Driver' -> 'HIF Driver' (hif_driver.sysml:81 `:>> efficiency = 0.35`).
    part def 'Base Driver' {
        attribute efficiency : Real;
    }

    part def 'Hif Driver' :> 'Base Driver' {
        // Subtype-DEF literal `:>>` — the (a) value, consumed cross-part by the
        // plant calc via the usage-level retype in the design.
        :>> efficiency = 0.35;
    }

    // Mechanism (b): target factory declares `cost_per_target` valueless; the plant
    // usage supplies it through a bare no-retype `part :>> target_factory { :>> ... }`
    // override block (the shape zero current fixtures contain — fusion-tea
    // hif_plant.sysml:36 `part :>> target_factory { :>> cost_per_target = 10.0; }`).
    part def 'Target Factory' {
        attribute cost_per_target : Real;
    }

    // Mechanism (c): a plain one-hop cross-part attribute. The reaction chamber declares
    // `cost_per_unit` (valueless on the def); the plant usage supplies its literal via a
    // usage-level DOTTED override (`:>> chamber.cost_per_unit = 7.0`, see design.sysml —
    // distinct from (b)'s override BLOCK). The plant calc reads `chamber.cost_per_unit`
    // cross-part; the current pipeline cannot wire the usage-level override to the inherited
    // calc input, so the entry point stays valueless TODAY (V11 trips) — while the captured
    // override literal (7.0, in hierarchy_data.design_overrides) is the value Item 2 flips
    // `chamber_cost` TO. NOT a trip-only offender.
    part def 'Reaction Chamber' {
        attribute cost_per_unit : Real;
    }

    // Base plant def: owns the base-typed subsystems, the cross-part consumer calc,
    // and the assert constraint. Mirrors fusion-tea 'IFE Power Plant': the consumer
    // and the subsystem parts are declared on the BASE def, and the design is a part
    // USAGE typed by this base with usage-level overrides/retypes.
    part def 'Power Plant' {
        // Subsystems (base-typed — the design retypes/overrides them).
        part driver : 'Base Driver';
        part target_factory : 'Target Factory';
        part chamber : 'Reaction Chamber';

        // Plant-level attribute for the self-named constraint binding below.
        attribute gain : Real = 40.0;

        // Cross-part consumer calc: each input reads a subsystem attr cross-part.
        calc cost_calc : PlantCostCalc {
            in driver_efficiency = driver.efficiency;              // (a)
            in target_cost = target_factory.cost_per_target;       // (b)
            in chamber_cost = chamber.cost_per_unit;               // (c) plain cross-part chain
        }

        attribute plant_cost : Real = cost_calc.plant_cost;

        // Assert constraint carrying three binding sub-shapes in one place
        // (Item 4/5 substrate; invisible to the drop report today — CONSTRAINT-SILENCE):
        //   - cross-part binding   : `in eta = driver.efficiency`
        //   - self-named binding   : `in gain = gain`
        //   - unbound defaulted param: `threshold` left unbound (uses default 10.0)
        assert constraint viability : 'Viability Threshold' {
            in eta = driver.efficiency;
            in gain = gain;
        }
    }
}
