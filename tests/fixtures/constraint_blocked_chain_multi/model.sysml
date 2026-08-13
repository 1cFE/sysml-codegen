package constraint_blocked_chain_multi {
    private import ScalarValues::*;

    // =====================================================================
    // Defect B: a predicate carrying more than one blocked feature chain.
    //
    // Three chain occurrences over two distinct references —
    // `bioshield.outer_radius` twice and `bioshield.inner_radius` once — so
    // the rendered detail must collapse to **two** entries, each naming its
    // own reference, its own rewrite, and its own location, in an order that
    // does not depend on the profile's walk.
    //
    // **Asserted, not plain.** The design's fixture plan called for a plain
    // constraint, on the reasoning that an asserted block halts before the
    // detail can be read. Measured, a *plain* constraint never consults the
    // profile at all — it grades `excluded` / `unassessed_form` and emits no
    // block reasons, so there would be no detail to read. The block reasons
    // exist only on the asserted path, and the way to read them without the
    // halt is the non-strict elaboration
    // (`test_elaboration_payload_identity.py:246-253`), which yields the same
    // SI_CONSTRAINT_BLOCKED diagnostic on a graph. The strict path is
    // asserted here too, so the same fixture pins that halting is unchanged.
    // The plain-and-blocked half of the Item 2 contract stays pinned by
    // `constraint_domain_plain_forms`.
    //
    // Chains stay blocked after this item. Only the message changes.
    //
    // **Source**: authored fixture (CONSTRAINT-SEMANTICS Item 4)
    // =====================================================================

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    part def Bioshield {
        attribute outer_radius : Real = 8.55;
        attribute inner_radius : Real = 6.0;
    }

    part def Plant {
        part bioshield : Bioshield;
        assert constraint layer_continuity {
            bioshield.outer_radius > 0.0
                and bioshield.inner_radius > 0.0
                and bioshield.outer_radius > 1.0
        }
    }

    part the_plant : Plant;
}
