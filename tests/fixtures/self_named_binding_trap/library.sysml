package TrapLib {
    private import ScalarValues::*;

    // Minimal calc whose input shares a name with the part attribute that feeds it.
    calc def AvailabilityCalc {
        doc /*
        Minimal calc for the self-named-binding trap (SC-5 mechanism D). Its input
        parameter is named identically to the part attribute bound to it, so the
        right-hand side of `in availability = availability` can resolve to the calc
        usage's OWN parameter (a self-reference) rather than the outer attribute.
        **Source**: authored fixture (Item 8, UPSTREAM-FINDINGS)
        **Reference**: spec.md Fixture 3 (self-named-binding trap, mechanism D)
        **Last Updated**: 2026-07-05
        */
        in attribute availability : Real;
        out attribute derated : Real = availability * 0.9;
    }

    part def 'Trap Plant' {
        doc /*
        Minimal part exercising exactly the mechanism-D self-named binding and
        nothing else, so its failure mode cannot be confounded. The binding
        `in availability = availability` names the RHS identically to the calc's
        own input parameter.
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 3 (isolation rationale)
        **Last Updated**: 2026-07-05
        */
        attribute availability : Real = 0.70;

        calc avail_calc : AvailabilityCalc {
            // Self-named binding (mechanism D): RHS shares the calc param's name.
            in availability = availability;
        }
    }
}
