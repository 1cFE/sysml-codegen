package nested_occurrence_override_probe {
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

    part def Panel {
        part source : Source;
        calc noop : Noop {
            in x = source.reading;
        }
        assert constraint within : 'Within Limit' {
            in v = source.reading;
        }
    }

    // KNOWN-INCOMPLETE PROBE (see PROVENANCE.md). The redefining `panel` usage is
    // nested inside an *instantiated* part def (`Design`), so the `:>>` override is
    // captured DEFINITION-relative (owning_part_qn = `..._Design__panel`) while demand
    // resolves OCCURRENCE-relative (instance_scope = `..._the_design__panel`). The
    // supplied-value materializer never matches the literal — 0 applied on BOTH the calc
    // and the constraint path — and strict generation halts on `source.reading`.
    part def Design {
        part panel : Panel {
            :>> source.reading = 80.0;
        }
    }
    part the_design : Design;
}
