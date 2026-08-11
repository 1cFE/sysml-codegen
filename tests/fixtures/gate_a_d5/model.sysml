package GateA {
    private import ScalarValues::*;

    // =====================================================================
    // Gate A fixture (Item 2, SR-A01/SR-R20/SR-R21).
    //
    // The real failure shape owner decision D-2 makes valid: a literal-valued
    // design attribute owned by a CONCRETE PartUsage, referenced by a
    // SELF-NAMED constraint actual, with no passthrough calculation anywhere.
    //
    // Why not `constraint_inline`: that fixture declares its attribute on the
    // part DEF, so it certifies a weaker shape (SR-R21).
    // Why def-typed and not inline: an inline constraint has no formal
    // bindings, so it never reaches resolution and would silently fail to
    // certify Gate A (design "Fixture shape constraint").
    //
    // **Source**: authored fixture (CONSTRAINT-LIFECYCLE-REMEDIATION Item 2)
    // **Reference**: design.md PC-1, spec.md SR-A01
    // =====================================================================

    constraint def 'Viability Threshold' {
        in attribute gain_in : Real;
        in attribute threshold : Real default 10.0;

        gain_in >= threshold
    }

    // The pipeline refuses a model with no calc definition at all
    // (`pipeline_builder.py:753`), so the fixture carries one. It is deliberately
    // UNRELATED to `gain` and to `the_host`: it neither produces nor consumes the
    // constrained attribute, so it is not the passthrough SR-A01 forbids and it
    // cannot mask the Gate A failure by minting `GateA__the_host__gain` itself.
    calc def Doubler {
        in attribute seed_in : Real;
        out attribute doubled : Real = seed_in * 2.0;
    }

    part def Unrelated {
        attribute seed : Real = 3.0;

        calc doubler : Doubler {
            in seed_in = seed;
        }
    }

    part the_other : Unrelated;

    part def Host;

    // The concrete PartUsage. `gain` is declared HERE, on the usage — not on
    // `Host`. Its owner walk reports the enclosing package as the owning
    // definition while the usage itself sits on `owner.owner`; that split is
    // the Gate A defect.
    part the_host : Host {
        attribute gain : Real = 40.0;

        assert constraint viability : 'Viability Threshold' {
            in gain_in = gain;
        }
    }
}
