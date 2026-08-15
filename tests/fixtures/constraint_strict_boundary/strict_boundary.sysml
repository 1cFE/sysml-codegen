package StrictBoundary {
    private import ScalarValues::*;

    // =====================================================================
    // The strict-comparison twin of `constraint_shared_polarity`. Boundary
    // behaviour is where a `>` / `>=` mix-up hides: at equality the two
    // operators disagree, and everywhere else they agree, so only the
    // equality sample can tell them apart. One shared definition typed twice
    // with opposite polarity, exactly as the inclusive fixture does, so the
    // two fixtures differ by the operator and by nothing else.
    //
    // Authored 2026-08-11 for recovery plan Gate 4C part 7 as the exact-route
    // execution specimen for the `strict-boundary` row of
    // `test_shared_definition_opposite_polarity_exact_once_execution`
    // (row L-192). D-5 binding form from the start.
    // =====================================================================

    calc def 'Margin Calc' {
        in attribute base_in : Real;
        out attribute m : Real = base_in - 1.0;
    }

    constraint def 'Above Bound' {
        in attribute m_in : Real;
        m_in > 0.0
    }

    part def Host {
        attribute rating : Real = 5.0;

        calc margin_calc : 'Margin Calc' {
            in base_in = rating;
        }

        assert constraint pos_bound : 'Above Bound' {
            in m_in = margin_calc.m;
        }

        assert not constraint neg_bound : 'Above Bound' {
            in m_in = margin_calc.m;
        }
    }

    part def Design {
        part h : Host;
    }
    part the_design : Design;
}
