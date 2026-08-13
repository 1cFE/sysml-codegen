package constraint_domain_plain_forms {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    // Two non-asserted forms whose predicates the mint must never walk. `blocked_if_asserted`
    // uses real-valued equality, which the executable profile BLOCKS -- as a bare `constraint`
    // it is not asserted, so it catalogs `excluded` / `unassessed_form` and generation
    // continues. `unreached_plain` sits on an owner with zero occurrences.
    part def Host {
        attribute value : Real = 5.0;
        constraint blocked_if_asserted {
            value == 5.0
        }
    }

    part def Detached {
        attribute other : Real = 1.0;
        constraint unreached_plain {
            other == 1.0
        }
    }

    part the_host : Host;
}
