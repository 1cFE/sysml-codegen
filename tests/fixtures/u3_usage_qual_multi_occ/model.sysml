package U3UsageQualMultiOcc {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — USAGE-qualified reference whose qualifying usage has TWO leaf
    // occurrences below the consumer (multiplicity 2). The consumer is a sibling of the
    // qualifying usage, so its own lineage does not own the slot. The leaf is
    // definition-owned, and the lineage miss refuses SI_OCCURRENCE_MISSING without
    // counting the two descendants.
    calc def AreaCalculation {
        in attribute length : Real;
        out attribute area : Real = length * 2.0;
    }

    part def 'Component' {
        attribute length : Real default 3.0;
    }

    part def 'Plant' {
        part component : 'Component'[2];

        calc area_calc : AreaCalculation {
            in length = component::length;
        }
    }

    part plant : 'Plant';
}
