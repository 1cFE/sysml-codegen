package TwoSameLeafLib {
    private import ScalarValues::*;

    // The ambiguous/defaulted producer coordinate (Item 10, contract acceptance row
    // "Ambiguous/defaulted producer resolution"). Two parts each own a `cost` design
    // attribute, so the bare leaf `cost` collides across scopes with no exact-QN
    // discriminator. A consumer that references the bare leaf must NOT be first-picked
    // to either candidate; the resolver refuses the tie and the producer-completeness
    // check names it.

    part def SubsystemA {
        // First same-leaf candidate.
        attribute cost : Real = 10.0;
    }

    part def SubsystemB {
        // Second same-leaf candidate — same leaf name, different scope.
        attribute cost : Real = 20.0;
    }

    // Consumer binding the bare leaf `cost` — the lenient name-based form that ties.
    calc def RollupConsumer {
        in attribute c : Real;
        out attribute total : Real = c + 1.0;
    }

    part def 'Ambiguous Plant' {
        part a : SubsystemA;
        part b : SubsystemB;

        // Bare-leaf reference — ambiguous across a.cost / b.cost. No instance scope to
        // disambiguate (contrast sibling_channel_ambiguity, which CAN disambiguate).
        calc consumer : RollupConsumer {
            in c = cost;
        }
    }
}
