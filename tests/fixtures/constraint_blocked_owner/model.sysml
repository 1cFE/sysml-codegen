package constraint_blocked_owner {
    private import ScalarValues::*;

    // A trivial calc def, unrelated to the assertion below: build_pipeline_context
    // requires at least one CalculationDefinition (Step 2) to build a full pipeline
    // context, and this fixture's whole point is a blocked-multiplicity assertion.
    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    // A constraint-owning part def reached only through a non-finite
    // multiplicity ([*]). occurrences_of("BlockedLeaf") must raise
    // NonFiniteCardinalityError -- lowering must surface this as a named
    // generation error (owner + feature), never a silent skip (Item 4's
    // audit cure exists precisely so this cannot be swallowed).
    //
    // A disjoint leaf type (mirroring instance_index_probe's BlockHost
    // pattern) keeps the fixture loadable -- `nonunique` shapes emit a
    // load-error diagnostic and are deliberately avoided here.
    part def BlockedLeaf {
        attribute reading : Real = 1.0;

        assert constraint nonneg {
            reading >= 0.0
        }
    }

    part def BlockHost {
        part star_member : BlockedLeaf [*];
    }

    part bhost : BlockHost;
}
