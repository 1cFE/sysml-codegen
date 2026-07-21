package CrossPartRollupLib {
    private import ScalarValues::*;

    // Per-child cost calc — each child instance owns one, producing a DISTINCT value so a
    // value coincidence can never mask a qualifier-drop collapse (the F2 lesson).
    calc def CostCalc {
        in attribute base : Real;
        out attribute cost : Real = base * 1.0;
    }

    // Subsystem: owns a cost calc and redefines its `capital` to that calc's output — the
    // stellarator's `part magnet : 'Magnet System' { :>> capital_cost = magnet_cost.capital_cost; }`
    // shape in miniature.
    part def Subsystem {
        attribute base : Real;
        calc cost_calc : CostCalc { in base = base; }
        attribute capital : Real;
    }

    // Downstream consumer — gives the pipeline a calc def and makes grand_total consumed.
    calc def FinalConsumer {
        in attribute t : Real;
        out attribute result : Real = t * 2.0;
    }

    part def 'Rollup Plant' {
        // Two same-type children with DIFFERENT bases → distinct per-instance capital.
        part a : Subsystem {
            :>> base = 3.0;
            :>> capital = cost_calc.cost;
        }
        part b : Subsystem {
            :>> base = 5.0;
            :>> capital = cost_calc.cost;
        }

        // Cross-part FORMULA sum of the two children's per-instance capital channels.
        // Correct = a.capital (3.0) + b.capital (5.0) = 8.0. A qualifier-drop collapse
        // (both terms → one child) would give 6.0 or 10.0 — detectable because 3 != 5.
        attribute grand_total : Real = a.capital + b.capital;

        // Consumer: result = 8.0 * 2.0 = 16.0
        calc final : FinalConsumer {
            in t = grand_total;
        }
    }
}
