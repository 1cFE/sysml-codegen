package predicate_unit_annotation_bare {
    private import ScalarValues::*;

    // =====================================================================
    // `predicate_unit_annotation` with every `[m]` removed.
    //
    // The asymmetry pin, mirroring `unit_annotation_lanes_bare`: one rule, so
    // the annotated and the bare spelling must produce the same module inputs
    // and the same values. If the annotated twin ever loses a dependency edge
    // the annotation was hiding, this comparison is what catches it
    // (design invariant 7).
    //
    // **Source**: authored fixture (CONSTRAINT-SEMANTICS Item 4)
    // =====================================================================

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    part def GapHost {
        attribute gap_width : Real = 0.5;
        assert constraint gap_guard {
            gap_width >= 0.25
        }
    }

    part the_host : GapHost;
}
