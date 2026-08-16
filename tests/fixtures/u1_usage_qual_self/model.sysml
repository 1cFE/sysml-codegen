package U1UsageQualSelf {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — the published USAGE-qualified spelling, copied structurally from
    // agentic_mbse_data/docs/patterns/adr002-calculations.md:100-110 and
    // expose-pattern.md:111-124: the qualifier names the ENCLOSING PART USAGE, and the
    // calc's formal shares the referent's name (so the qualifier is load-bearing —
    // a bare `length` here would be a self-binding).
    calc def AreaCalculation {
        in attribute length : Real;
        in attribute width : Real;
        out attribute area : Real = length * width;
    }

    part component {
        attribute length : Real = 3.0;
        attribute width : Real = 4.0;

        calc area_calc : AreaCalculation {
            in length = component::length;
            in width = component::width;
        }

        attribute total_area : Real = area_calc.area;
    }
}
