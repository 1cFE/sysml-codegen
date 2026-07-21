package constraint_inline {
    private import ScalarValues::*;

    // A trivial calc def, unrelated to the assertion below: build_pipeline_context
    // requires at least one CalculationDefinition (Step 2) to build a full pipeline
    // context, and this fixture's whole point is a calc-free assertion.
    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    // No named constraint def: the assertion owns its predicate inline
    // (ConstraintSource.form == "inline"), so the effective predicate comes
    // from the usage itself, not a definition. Single instance is enough --
    // the point is the source-form axis, not expansion cardinality.
    part def InlineHost {
        attribute value : Real = 5.0;
        assert constraint positive {
            value > 0.0
        }
    }

    part the_host : InlineHost;
}
