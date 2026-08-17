package U2UsageQualTwoOwnerOcc {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — the published USAGE-qualified spelling authored inside a part
    // DEFINITION that has TWO occurrences, so two occurrences of the qualifying usage
    // `component` exist. The resolved leaf remains definition-owned. Each consumer is
    // above its component occurrence, so both references refuse SI_OCCURRENCE_MISSING.
    calc def AreaCalculation {
        in attribute length : Real;
        out attribute area : Real = length * 2.0;
    }

    part def 'Component' {
        attribute length : Real default 3.0;
    }

    part def 'Plant' {
        part component : 'Component';

        calc area_calc : AreaCalculation {
            in length = component::length;
        }
    }

    part plant_a : 'Plant' {
        part :>> component { :>> length = 11.0; }
    }

    part plant_b : 'Plant' {
        part :>> component { :>> length = 99.0; }
    }
}
