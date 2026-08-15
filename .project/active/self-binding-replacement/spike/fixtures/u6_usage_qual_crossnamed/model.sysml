package U6UsageQualCrossnamed {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — the sharpest test of whether the usage qualifier is load-bearing.
    // The consumer is authored INSIDE `comp_b` (length 7.0) but explicitly names
    // `comp_a::length` (length 3.0). The written reference means 3.0 and nothing else.
    // If the route resolves positionally off the consumer's own lineage, it will deliver
    // 7.0 with no diagnostic.
    calc def AreaCalculation {
        in attribute length_in : Real;
        out attribute area : Real = length_in * 2.0;
    }

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' { :>> length = 3.0; }

        part comp_b : 'Component' {
            :>> length = 7.0;

            // The author means comp_a's 3.0.
            calc area_calc : AreaCalculation {
                in length_in = comp_a::length;
            }
        }
    }

    part plant : 'Plant';
}
