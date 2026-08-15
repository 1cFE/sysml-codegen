package UnitAnnotationLanesBare {
    private import ScalarValues::*;
    private import SI::*;

    // =====================================================================
    // Both spellings of a unit annotation, in one model, so the asymmetry
    // between them cannot come back silently.
    //
    //   `default 40.0` on a calc-def formal — the lane that always worked
    //                      (modeled_default_fidelity, DD-A11 / DD-A12).
    //   `= 0.5`        on an attribute value — the lane that refused with
    //                      SI_OCCURRENCE_MISSING against `SI::metre`, because
    //                      the unit reached the reference walk and the feature
    //                      slot index holds only the user model's features.
    //
    // A unit annotation contributes its value and never a reference. The
    // companion fixture `unit_annotation_lanes_bare` is this model with the
    // annotations removed; both must resolve to the same values.
    //
    // **Source**: authored fixture (cutover recovery, Gate 4C part 6)
    // =====================================================================

    calc def Rated {
        in attribute thickness : Real;
        in attribute rated_power : Real default 40.0;
        out attribute figure : Real = thickness * rated_power;
    }

    part def Layer { attribute thickness : Real = 0.5; }
    part def Stack;

    part the_stack : Stack {
        part layer_a : Layer;
        calc rated_calc : Rated {
            in thickness = layer_a::thickness;
        }
    }
}
