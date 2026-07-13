package constraint_multi_instance {
    private import ScalarValues::*;

    calc def 'Power Calc' {
        in attribute r : Real;
        out attribute p : Real = r * 2.0;
    }

    constraint def 'Nonneg Power' {
        in attribute p : Real;
        p >= 0.0
    }

    // Cell owns its own calc AND its own assertion (self-scoped: the actual
    // `power_calc.p` is a sibling feature reference, no cross-part chain
    // needed). This is what makes part_def-owner expansion (occurrences_of
    // Cell) produce three concrete constraints -- one per Cell occurrence --
    // each resolving its own `power_calc.p` in its own occurrence scope.
    part def Cell {
        attribute cell_rating : Real = 10.0;
        calc power_calc : 'Power Calc' {
            in r = cell_rating;
        }
        assert constraint nonneg : 'Nonneg Power' {
            in p = power_calc.p;
        }
    }

    part def Container {
        part cell : Cell [3];
    }

    // A package-level design instance is required for instantiation-path
    // discovery -- a def-only model drops the template calc entirely
    // ("no PartUsage instantiations", b1-probe-evidence.md).
    part def Design {
        part c : Container;
    }
    part the_design : Design;
}
