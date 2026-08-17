package U3BUsageQualSingleOcc {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — the multiplicity-1 control for u3. Same topology, one occurrence
    // of the qualifying usage. The sole descendant is still not on the consumer's lineage,
    // so the definition-owned leaf refuses SI_OCCURRENCE_MISSING.
    calc def AreaCalculation {
        in attribute length : Real;
        out attribute area : Real = length * 2.0;
    }

    part def 'Component' {
        attribute length : Real default 3.0;
    }

    part def 'Plant' {
        part component : 'Component'[1];

        calc area_calc : AreaCalculation {
            in length = component::length;
        }
    }

    part plant : 'Plant';
}
