// D3-7: two PartDefs named `Widget` in DIFFERENT packages, each carrying a
// FORMULA computed attribute named `result`. The attribute resolution map in
// graph_builder keys buckets by the BARE owning_part_name ("Widget"), so both
// parts collapse into a single bucket and same-named attrs overwrite.
package D37PkgA {
    private import ScalarValues::*;

    part def Widget {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        attribute result : Real = a * b;   // FORMULA (siblings only)
    }
}

package D37PkgB {
    private import ScalarValues::*;

    part def Widget {
        attribute a : Real = 10.0;
        attribute b : Real = 20.0;
        attribute result : Real = a + b;   // FORMULA (siblings only)
    }
}

// Minimal calc def so build_pipeline_context accepts the model (probe-runnability
// gate). Isolated from the two Widget FORMULA attrs that D3-7 exercises.
package D37Probe {
    private import ScalarValues::*;
    calc def NoopCalc {
        in attribute x : Real;
        out attribute result : Real = x;
    }
}
