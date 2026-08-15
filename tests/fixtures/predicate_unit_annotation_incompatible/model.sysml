package predicate_unit_annotation_incompatible {
    private import ScalarValues::*;
    private import SI::*;

    // =====================================================================
    // `predicate_unit_annotation` with a dimensionally incompatible
    // annotation: a length compared against a time.
    //
    //   `gap_width [m] >= 0.25 [s]`
    //
    // This is a **regression guard on the companion path**, not a
    // discriminator for the codegen fix (design review A1): the profile's
    // verdict is computed at elaborate.py:403 from the companion's own
    // extraction, before and independent of the reference walk the fix
    // touches. It pins "carried, never applied" — suppressing the unit as a
    // *data reference* must not suppress it as a *unit*, so the profile must
    // still see a unit here and still refuse.
    //
    // Asserted, so the profile is actually consulted: a plain constraint
    // grades `excluded` / `unassessed_form` without the profile ever running,
    // which would pin nothing. The block therefore halts elaboration, and the
    // dimension reason is read off the refusal.
    //
    // **Source**: authored fixture (CONSTRAINT-SEMANTICS Item 4)
    // =====================================================================

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    part def GapHost {
        attribute gap_width : Real = 0.5 [m];
        assert constraint gap_guard {
            gap_width [m] >= 0.25 [s]
        }
    }

    part the_host : GapHost;
}
