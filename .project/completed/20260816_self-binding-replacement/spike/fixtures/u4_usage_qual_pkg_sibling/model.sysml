package U4UsageQualPkgSibling {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — USAGE-qualified reference naming a PACKAGE-LEVEL usage from
    // inside a different part definition. The qualifier is in lexical scope, but the
    // named occurrence is a top-level sibling of the consumer's own occurrence, not a
    // descendant of any shared ancestor.
    calc def AreaCalculation {
        in attribute length : Real;
        out attribute area : Real = length * 2.0;
    }

    part def 'Component' {
        attribute length : Real default 3.0;
    }

    part shared_component : 'Component' {
        :>> length = 42.0;
    }

    part def 'Plant' {
        calc area_calc : AreaCalculation {
            in length = shared_component::length;
        }
    }

    part plant : 'Plant';
}
