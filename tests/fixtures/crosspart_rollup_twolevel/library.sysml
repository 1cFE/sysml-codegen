package CrossPartRollupLib {
    private import ScalarValues::*;

    // Two-level cross-part aggregation — the stellarator capital-rollup shape in
    // miniature (Item 10, A7). `group_one` is an inner cross-part sum (an aggregation);
    // `grand_total` references that inner aggregation (a LocalTerm) PLUS another
    // cross-part chain (a SingletonTerm) — an aggregation whose operand is itself an
    // aggregation output. This proves the A7 registration precondition: the inner
    // aggregation's canonical channel must be registered before the outer LocalTerm
    // resolves, or the outer silently mints an entry point (the F4-cutover collapse).

    part def SubsystemA {
        attribute cost : Real = 3.0;
    }

    part def SubsystemB {
        attribute cost : Real = 5.0;
    }

    part def SubsystemC {
        attribute cost : Real = 7.0;
    }

    // Downstream consumer of the outer rollup — gives the pipeline a calc def and makes
    // grand_total a consumed value (so the LocalTerm chain is exercised end to end).
    calc def FinalConsumer {
        in attribute t : Real;
        out attribute result : Real = t * 2.0;
    }

    part def 'Rollup Plant' {
        part a : SubsystemA;
        part b : SubsystemB;
        part c : SubsystemC;

        // Inner aggregation: cross-part sum of two sibling parts' cost channels.
        // = 3.0 + 5.0 = 8.0
        attribute group_one : Real = a.cost + b.cost;

        // Outer aggregation: inner-aggregation output (group_one, a LocalTerm) plus a
        // third cross-part chain (c.cost, a SingletonTerm). = 8.0 + 7.0 = 15.0
        attribute grand_total : Real = group_one + c.cost;

        // Consumer: reads the outer rollup. result = 15.0 * 2.0 = 30.0
        calc final : FinalConsumer {
            in t = grand_total;
        }
    }
}
