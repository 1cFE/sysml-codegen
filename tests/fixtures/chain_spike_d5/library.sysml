package ChainSpikeLibrary {
    private import ScalarValues::Real;

    calc def AreaCalc {
        in attribute length_in : Real;
        in attribute width_in : Real;

        out attribute area : Real = length_in * width_in;
    }

    calc def CostCalc {
        in attribute area : Real;
        in attribute rate_in : Real;

        out attribute total_cost : Real = area * rate_in;
    }

    calc def SummaryCalc {
        in attribute area : Real;
        in attribute cost : Real;

        out attribute cost_per_area : Real = cost / area;
    }
}
