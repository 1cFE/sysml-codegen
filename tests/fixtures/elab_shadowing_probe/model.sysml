package ElabShadowingProbe {
    private import ScalarValues::*;

    // =====================================================================
    // The two capability-survey evidence gaps (ELABORATE-FIRST Item 5,
    // Phase 2 shadowing leg — plan.md; research
    // 20260807-145336_elaborate-first-instance-graph-architecture.md):
    //
    // 1. SPECIALIZATION SHADOWING: a two-level def chain where BOTH levels
    //    redefine the same inherited attribute with literals. The innermost
    //    definition must win per occurrence (Leaf's 9.0 at a Leaf occurrence,
    //    Mid's 5.0 at a Mid occurrence) — all three values differ so a wrong
    //    pick is visible by construction.
    //
    // 2. EQUAL-VALUED INDEPENDENT LITERALS: two occurrences overriding the
    //    same attribute to the SAME value. The contract's ratified rule
    //    (2026-08-05): distinct occurrences are distinct sources even when
    //    values coincide — one node each, never shared.
    //
    // Authoring constraint (SysIDE feature-value-overriding): a `:>>` cannot
    // override a BOUND (`=`) value, so every overridable level uses `default`
    // — the base declarations and Mid's redefinition below.
    //
    // **Source**: authored fixture (ELABORATE-FIRST Item 5, shadowing leg)
    // =====================================================================

    calc def Consume {
        in attribute v : Real;
        out attribute out_v : Real = v * 2.0;
    }

    // ---- shape 1: two-level specialized-def literal shadowing --------------
    part def Base {
        attribute rate : Real default 1.0;
        // Def-authored consumer on the BASE: at a Leaf occurrence it must read
        // the innermost redefined value.
        calc base_calc : Consume {
            in v = rate;
        }
    }

    part def Mid :> Base {
        :>> rate default 5.0;
    }

    part def Leaf :> Mid {
        :>> rate = 9.0;
    }

    part the_mid : Mid;
    part the_leaf : Leaf;

    // ---- shape 2: equal-valued independent occurrence literals -------------
    part def Thing {
        attribute x : Real default 4.0;
        calc thing_calc : Consume {
            in v = x;
        }
    }

    part t1 : Thing {
        :>> x = 4.0;
    }
    part t2 : Thing {
        :>> x = 4.0;
    }
}
