package constraint_binding_unit_annotation {
    private import ScalarValues::*;
    private import SI::*;

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
    // `bad_band` is the bound: a *genuine* expression source (`a + b`) has an
    // operator that is not `[`, passes through the unwrap unchanged, and is
    // still refused. The cure admits two shapes, not arithmetic.
    //
    // Both usages are plain, not asserted, so a profile block catalogs
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

    part def Host {
        attribute other_feature : Real = 1.0;
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;

        constraint band : BandGuard {
            in ref_value = other_feature [m];
            in tol = 0.05 [m];
        }

        constraint bad_band : BandGuard {
            in ref_value = other_feature;
            in tol = a + b;
        }
    }

    part the_host : Host;
}
