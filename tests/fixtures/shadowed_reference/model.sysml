package ShadowedReference {
    private import ScalarValues::*;

    // =====================================================================
    // Same-named attributes at two scopes, with DIFFERENT values (Item 4,
    // audit F2). The discriminating fixture: catf_mfe's real instance of this
    // shape was masked for a whole audit cycle because both attributes held
    // 3.0, so every value gate passed while the binding silently re-anchored.
    //
    // `outer.scale` is 2.0 and `inner.scale` is 7.0. A `::`-qualified reference
    // to the outer one that gets re-anchored under the consumer's own owner
    // selects the inner one, and the value moves — visibly, by construction.
    //
    // **Source**: authored fixture (CONSTRAINT-LIFECYCLE-REMEDIATION Item 4)
    // **Reference**: audit.md F2; evidence PC-7
    // =====================================================================

    calc def Scale {
        in attribute factor : Real;
        out attribute scaled : Real = factor * 10.0;
    }

    part def Inner;
    part def Outer;

    part the_outer : Outer {
        attribute scale : Real = 2.0;

        part inner : Inner {
            // A local shadow of the SAME name, deliberately a DIFFERENT value.
            attribute scale : Real = 7.0;

            // Written `::`-qualified against the OUTER scope. The model means
            // 2.0. Re-anchoring the bare leaf under `the_outer__inner` would
            // select the 7.0 shadow.
            calc shadowed_calc : Scale {
                in factor = ShadowedReference::the_outer::scale;
            }
        }
    }
}
