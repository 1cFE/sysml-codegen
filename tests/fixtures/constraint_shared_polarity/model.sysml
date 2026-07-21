package constraint_shared_polarity {
    private import ScalarValues::*;

    calc def 'Margin Calc' {
        in attribute base : Real;
        out attribute m : Real = base - 1.0;
    }

    // ONE shared constraint definition -- compiled once to a single neutral
    // predicate body (`m >= 0.0`). The two usages below type this same
    // definition with opposite polarity; each retains its own margin sign.
    constraint def 'Within Bound' {
        in attribute m : Real;
        m >= 0.0
    }

    part def Host {
        attribute rating : Real = 5.0;
        calc margin_calc : 'Margin Calc' {
            in base = rating;
        }
        // Positive usage of the shared definition: satisfied when m >= 0.
        assert constraint pos_bound : 'Within Bound' {
            in m = margin_calc.m;
        }
        // Negated usage of the SAME definition (polarity flips). Its margin
        // sign must come from this usage's own polarity, not from whichever
        // catalog entry sorts first (invariant 29). One neutral predicate body,
        // two independent polarities.
        assert not constraint neg_bound : 'Within Bound' {
            in m = margin_calc.m;
        }
    }

    // Package-level design instance for instantiation-path discovery.
    part def Design {
        part h : Host;
    }
    part the_design : Design;
}
