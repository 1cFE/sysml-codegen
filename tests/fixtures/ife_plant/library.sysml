package IfePlantLib {
    private import ScalarValues::*;

    // =====================================================================
    // Template calcs (calc def belongs in library — ADR-002)
    // =====================================================================

    // Plant-level calc consuming the 14 def-declared plant literals (shape 1).
    // A representative closed form — not the full Hawker DCF; the point is that
    // the 14 literals feed a calc so Item 9 measures a real pre-fill surface.
    calc def PlantLcoe {
        doc /*
        Representative plant LCOE-style calc consuming the 14 technology-agnostic
        parameters. Simplified formula — the modeling shape (14 def literals wired
        to a calc) is what Item 9 measures, not the economics.

        **Source**: authored fixture (Item 8, UPSTREAM-FINDINGS)
        **Reference**: spec.md Fixture 2, shape 1 (richness floor)
        **Last Updated**: 2026-07-05
        */
        in attribute availability : Real;
        in attribute frequency : Real;
        in attribute gain : Real;
        in attribute thermal_efficiency : Real;
        in attribute discount_rate : Real;
        in attribute plant_cost_constant : Real;
        in attribute om_cost_constant : Real;
        in attribute blanket_energy_multiple : Real;
        in attribute driver_cost_constant : Real;
        in attribute driver_efficiency : Real;
        in attribute driver_energy : Real;
        in attribute driver_lifetime_shots : Real;
        in attribute target_cost_constant : Real;
        in attribute yield_cost_constant : Real;

        out attribute lcoe : Real =
            (plant_cost_constant + om_cost_constant + target_cost_constant)
            / (availability * gain * driver_efficiency * thermal_efficiency);
    }

    // Base-driver template calc (supertype owns it — preserved under retyping).
    calc def DriverPowerCalc {
        doc /*
        Driver electrical power from wall-plug efficiency and bank energy.
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 3 (supertype-preserved template)
        **Last Updated**: 2026-07-05
        */
        in attribute efficiency : Real;
        in attribute bank_energy : Real;
        out attribute driver_power : Real = efficiency * bank_energy;
    }

    // Subtype-driver template calc (shape 3: retyped part instantiates THIS).
    calc def HifCostCalc {
        doc /*
        HIF driver capital cost from cost-per-joule and bank energy.
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 3 (subtype template instantiates)
        **Last Updated**: 2026-07-05
        */
        in attribute cost_per_joule : Real;
        in attribute bank_energy : Real;
        out attribute driver_cost : Real = cost_per_joule * bank_energy;
    }

    // Chamber template calc (shape 7: two same-type siblings each own an instance).
    calc def ChamberYieldCalc {
        doc /*
        Chamber yield cost from blanket multiple and yield constant.
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 7 (per-instance sibling calc)
        **Last Updated**: 2026-07-05
        */
        in attribute blanket_multiple : Real;
        in attribute yield_constant : Real;
        out attribute chamber_yield : Real = blanket_multiple * yield_constant;
    }

    // Coil volume calc (a calc output that shape 4 reaches THROUGH a nested part).
    calc def CoilVolume {
        doc /*
        Coil volume from radius — the calc output that the shape-4 cross-part
        chain reaches through the nested tf_coil part.
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 4 (cross-part chain target)
        **Last Updated**: 2026-07-05
        */
        in attribute radius : Real;
        out attribute volume : Real = radius * radius * 3.14159;
    }

    // Cryogenic-load calc consuming a cross-part magnet volume (shape 4). Mirrors
    // catf_mfe's cryo_load: its magnet_volume input is bound cross-part to a
    // SIBLING usage's exposed calc output and is deliberately left unwired
    // (mechanism B, known-incomplete — expected to trip V11 on the strict path).
    calc def CryoLoad {
        doc /*
        Cryogenic cooling load from magnet volume. Its input is wired cross-part
        (mechanism B) and deliberately left unresolvable — the known-incomplete
        baseline Items 9-10 later wire.
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 4 (cross-part chain, unwired)
        **Last Updated**: 2026-07-05
        */
        in attribute magnet_volume : Real;
        out attribute cooling_power : Real = magnet_volume * 0.05;
    }

    // =====================================================================
    // Subsystem part defs
    // =====================================================================

    // Base for shape 2 (a specialized def sets its literal via :>>).
    part def 'Power Core' {
        doc /*
        Base power-core subsystem carrying a scope-multiplier attribute that a
        specialized subsystem def redefines via :>> (shape 2, mechanism A).
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 2 (:>>-valued specialized def)
        **Last Updated**: 2026-07-05
        */
        attribute scope_multiplier : Real;
    }

    // Shape 2: specialize the base and set its def-declared attribute via :>>.
    // Mechanism A — the :>>-set value on the specialized DEF is known-incomplete
    // at extraction.
    part def 'Shielded Core' :> 'Power Core' {
        doc /*
        Shielded power-core specialization. Sets the inherited scope_multiplier
        via :>> on the DEF (shape 2, mechanism A — known-incomplete baseline).
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 2
        **Last Updated**: 2026-07-05
        */
        :>> scope_multiplier = 3.0;
    }

    // Coil: exposes a calc-derived volume (the shape-4 chain reaches this output
    // through the nested tf_coil part in the design).
    part def 'Coil' {
        doc /*
        Toroidal-field coil. Its volume is a calc output exposed as an attribute;
        the shape-4 cross-part chain reaches this calc output through the coil.
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 4 (calc output reached through part)
        **Last Updated**: 2026-07-05
        */
        attribute radius : Real = 4.0;
        calc volume_calc : CoilVolume {
            in radius = radius;
        }
        attribute volume : Real = volume_calc.volume;
    }

    // Supertype driver: owns the base-power template calc.
    part def 'Base Driver' {
        doc /*
        Abstract-style base IFE driver. Owns the base-power template calc that is
        PRESERVED when a nested driver part is retyped to a subtype (shape 3).
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 3
        **Last Updated**: 2026-07-05
        */
        attribute efficiency : Real = 0.10;
        attribute bank_energy : Real = 10000000.0;

        calc base_power_calc : DriverPowerCalc {
            in efficiency = efficiency;
            in bank_energy = bank_energy;
        }
    }

    // Subtype driver :> 'Base Driver': owns its own template calc (hif_cost_calc).
    // Shape 3: a nested part retyped to this instantiates hif_cost_calc (subtype)
    // AND base_power_calc (supertype, preserved) — the Item 4/5 win.
    part def 'Hif Driver' :> 'Base Driver' {
        doc /*
        HIF driver specialization. Owns its own cost template calc; when a nested
        driver part is retyped to this subtype, hif_cost_calc instantiates
        (shape 3, the working retype path).
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 3 (subtype template instantiates)
        **Last Updated**: 2026-07-05
        */
        attribute cost_per_joule : Real = 5.0;

        calc hif_cost_calc : HifCostCalc {
            in cost_per_joule = cost_per_joule;
            in bank_energy = bank_energy;
        }
    }

    // Chamber: owns a template calc so each sibling usage produces its own
    // instance-scoped virtual calc (shape 7).
    part def 'Reaction Chamber' {
        doc /*
        IFE reaction chamber. Owns a yield template calc; two same-type sibling
        chamber usages on the plant each produce their own virtual CalcUsage
        (shape 7, the instance-ambiguity substrate for Item 10).
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 7 (two same-type siblings)
        **Last Updated**: 2026-07-05
        */
        attribute blanket_multiple : Real = 1.2;
        attribute yield_constant : Real = 5000000.0;

        calc yield_calc : ChamberYieldCalc {
            in blanket_multiple = blanket_multiple;
            in yield_constant = yield_constant;
        }
    }

    // =====================================================================
    // The generic plant part def (shape 1: >=14 def-declared literals)
    // =====================================================================

    part def 'Ife Power Plant' {
        doc /*
        Generic IFE power plant. Carries the 14 technology-agnostic Hawker
        parameters as DEF-DECLARED attribute literals (shape 1, richness floor)
        wired to the PlantLcoe calc, plus:
          - a base driver nested part (retyped to a subtype in the design, shape 3),
          - two same-type sibling chambers (shape 7),
          - a shielded-core subsystem (shape 2),
          - a cross-part power-balance calc left deliberately unwired (shape 4).
        **Source**: authored fixture (Item 8), shaped after fusion-tea ife_plant
        **Reference**: spec.md Fixture 2 shape table
        **Last Updated**: 2026-07-05
        */

        // === 14 def-declared literals (shape 1 richness floor) ===
        attribute availability : Real = 0.70;
        attribute frequency : Real = 0.2;
        attribute gain : Real = 500.0;
        attribute thermal_efficiency : Real = 0.40;
        attribute discount_rate : Real = 0.08;
        attribute plant_cost_constant : Real = 3000.0;
        attribute om_cost_constant : Real = 30.0;
        attribute blanket_energy_multiple : Real = 1.2;
        attribute driver_cost_constant : Real = 5.0;
        attribute driver_efficiency : Real = 0.10;
        attribute driver_energy : Real = 10000000.0;
        attribute driver_lifetime_shots : Real = 50000000.0;
        attribute target_cost_constant : Real = 10.0;
        attribute yield_cost_constant : Real = 5000000.0;

        // A 15th literal + an overridable target for shape 5 (mechanism C).
        attribute net_power_target : Real = 1000.0;
        attribute capacity_factor : Real default := 0.90;

        // === Nested subsystem parts ===
        part driver : 'Base Driver';
        part core : 'Shielded Core';
        // Shape 7: two same-type sibling chambers.
        part chamber_a : 'Reaction Chamber';
        part chamber_b : 'Reaction Chamber';

        // === Plant-level LCOE calc (14 def literals wired to the calc) ===
        calc lcoe_calc : PlantLcoe {
            in availability = availability;
            in frequency = frequency;
            in gain = gain;
            in thermal_efficiency = thermal_efficiency;
            in discount_rate = discount_rate;
            in plant_cost_constant = plant_cost_constant;
            in om_cost_constant = om_cost_constant;
            in blanket_energy_multiple = blanket_energy_multiple;
            in driver_cost_constant = driver_cost_constant;
            in driver_efficiency = driver_efficiency;
            in driver_energy = driver_energy;
            in driver_lifetime_shots = driver_lifetime_shots;
            in target_cost_constant = target_cost_constant;
            in yield_cost_constant = yield_cost_constant;
        }

        attribute lcoe : Real = lcoe_calc.lcoe;
    }
}
