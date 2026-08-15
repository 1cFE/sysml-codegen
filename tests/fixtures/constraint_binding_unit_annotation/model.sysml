package constraint_binding_unit_annotation {
    private import ScalarValues::*;
    private import SI::*;
    private import NumericalFunctions::sum;

    // =====================================================================
    // The fourth lane: a unit annotation on a *constraint usage binding*.
    //
    //   `in tol = 0.05 [m];`        — the annotated literal   (D2 shape i)
    //   `in ref_value = other_feature [m];` — the annotated reference (D2 shape ii)
    //
    // `_binding_evidence` classifies chain → reference → literal → else
    // expression. An annotation is an OperatorExpression, so before the cure
    // both fell through to `expression_evidence` and were refused as
    // SI_EXPRESSION_SOURCE_UNSUPPORTED rather than read as the value `0.05`
    // and as a reference to `other_feature`.
    //
    // This lane sits directly on Item 5's blessed tolerance-band recipe and
    // on the rewrite Defect B's new message advertises, so it must be a
    // supported form.
    //
    // `bad_band` and `invoked_band` are the bound, on both sides of the line
    // the design drew. A *genuine* expression source has an operator that is
    // not `[`, so it passes through the unwrap unchanged and is still refused:
    // arithmetic (`a + b`) and an invocation (`sum(other_feature)`) both. The
    // cure admits annotations, not expressions.
    //
    // `chain_band` is the other edge of shape (ii): an annotated *chain*
    // (`cell.reading [m]`). The unwrap contributes the chain, so it classifies
    // as a chain binding and resolves, rather than falling to
    // `expression_evidence`. Named in the design's admitted set and otherwise
    // untested.
    //
    // Every usage is plain, not asserted, so a profile block catalogs
    // instead of halting and the bindings can be read off the graph.
    //
    // **Source**: authored fixture (CONSTRAINT-SEMANTICS Item 4)
    // =====================================================================

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def BandGuard {
        in attribute ref_value : Real;
        in attribute tol : Real;
        ref_value >= tol
    }

    part def Cell {
        attribute reading : Real = 2.0;
    }

    part def Host {
        attribute other_feature : Real = 1.0;
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        part cell : Cell;

        constraint band : BandGuard {
            in ref_value = other_feature [m];
            in tol = 0.05 [m];
        }

        constraint bad_band : BandGuard {
            in ref_value = other_feature;
            in tol = a + b;
        }

        constraint invoked_band : BandGuard {
            in ref_value = other_feature;
            in tol = sum(other_feature);
        }

        constraint chain_band : BandGuard {
            in ref_value = cell.reading [m];
            in tol = 0.05 [m];
        }
    }

    part the_host : Host;
}
