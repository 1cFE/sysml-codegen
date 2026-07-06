package SiblingLib {
    private import ScalarValues::*;

    // Producer calc owned by each chamber. Two same-type sibling chambers each own
    // an instance of this calc, so its output `power` exists twice under different
    // instance paths — the collision the consumer must disambiguate (SC-3).
    calc def PowerCalc {
        doc /*
        Producer for the sibling-ambiguity test (SC-3). Two same-type chambers each
        own a power_calc, so `power_calc.power` collides on the flat alias; the
        consumer binding must resolve to the correct instance-scoped channel
        (chamber_b's), not first-wins to chamber_a.
        **Source**: authored fixture (Item 10, UPSTREAM-FINDINGS stage (b))
        **Reference**: spec.md SC-3 (instance-ambiguity channel test)
        **Last Updated**: 2026-07-05
        */
        in attribute fuel : Real;
        out attribute power : Real = fuel * 10.0;
    }

    // Cross-part consumer. It binds chamber_b's power specifically; the resolver must
    // route to chamber_b's instance-scoped channel, not chamber_a's.
    calc def TotalCalc {
        in attribute chamber_power : Real;
        out attribute total : Real = chamber_power + 1.0;
    }

    part def Chamber {
        attribute fuel : Real = 2.0;

        calc power_calc : PowerCalc {
            in fuel = fuel;
        }

        // Expose the calc output as a part attribute. Both siblings expose `power`,
        // so the flat alias `power` collides; only the instance-scoped channel
        // (chamber_a.power vs chamber_b.power) disambiguates.
        attribute power : Real = power_calc.power;
    }

    part def 'Twin Plant' {
        // Two same-type siblings: both expose a `power` attribute.
        part chamber_a : Chamber;
        part chamber_b : Chamber;

        // Consumer disambiguates to chamber_b's instance-scoped power channel.
        calc total_calc : TotalCalc {
            in chamber_power = chamber_b.power;
        }
    }
}
