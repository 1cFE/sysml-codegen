package constraint_def_owned_redefining {
    private import ScalarValues::*;

    part def Source {
        attribute reading : Real;
    }

    // build_pipeline_context requires at least one CalculationDefinition.
    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def 'Within Limit' {
        in attribute v : Real;
        v <= 100.0
    }

    // The DEFINITION owns the assertion (typed by the shared constraint def).
    // Its actual is a nested design attribute, declared without a value binding
    // so a usage may redefine it.
    part def Panel {
        part source : Source;
        calc noop : Noop {
            in x = source.reading;
        }
        assert constraint within : 'Within Limit' {
            in v = source.reading;
        }
    }

    // Redefining usage: this package-level occurrence of Panel redefines the
    // actual via `:>>`. The definition-owned assert SOURCE (Panel::within, typed
    // by 'Within Limit') and this redefining occurrence's actual identity
    // (constraint_def_owned_redefining__panel__source__reading) remain distinct
    // (invariant 27); reading = 80.0 satisfies `v <= 100.0`, so the expected
    // verdict is satisfied. The redefined attribute resolves under exact identity
    // like any design attribute (shared resolver row 16, occurrence_materialized_qn).
    part panel : Panel {
        :>> source.reading = 80.0;
    }
}
