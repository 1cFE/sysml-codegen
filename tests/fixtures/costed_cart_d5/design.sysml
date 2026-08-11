package CostedCartDesign {
    doc /*
    The concrete cart instance: every leaf driver bound, plus the two
    system-level calc usages.

    Both system calc usages are in the D-5 form (``in <formal>_in = <attr>``),
    which is what lets the exact route elaborate this model. The values are
    chosen so the hand arithmetic in the Gate 4C specimens is exact in binary
    floating point.

    **Source**: authored for recovery plan Gate 4C, rows L-199/L-203/L-198/L-201
    **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
    **Last Updated**: 2026-08-11
    */

    private import ScalarValues::Real;
    private import CostedCartLibrary::*;

    part cart_plant : 'Cart Plant' {

        part redefines deck_assembly : 'Deck Assembly' {
            :>> deck_panel.area = 2.5;
            :>> caster.load_rating = 80.0;
        }

        part redefines frame_assembly : 'Frame Assembly' {
            :>> frame_rail.length = 4.0;
            :>> cross_brace.brace_count = 6.0;
        }

        // Operating parameters.
        attribute recovery_factor : Real = 0.1;
        attribute shift_count : Real = 3.0;
        attribute units_per_shift : Real = 250.0;
        attribute handling_cost_per_unit : Real = 0.4;

        // FORMULA computed attribute over same-part siblings. Its module output
        // is what the throughput calc usage below consumes.
        attribute throughput_units : Real = shift_count * units_per_shift;

        calc annualized_financial : AnnualizedFinancialCalc {
            in total_capex_in = capital_cost;
            in recovery_factor_in = recovery_factor;
        }

        calc annual_handling : ThroughputCostCalc {
            in throughput_units_in = throughput_units;
            in handling_cost_per_unit_in = handling_cost_per_unit;
        }
    }
}
