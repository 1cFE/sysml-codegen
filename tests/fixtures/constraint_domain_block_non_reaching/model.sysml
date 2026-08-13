package constraint_domain_block_non_reaching {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    // A BLOCK profile decision (real-valued equality) on an asserted usage that reaches
    // no instance. `SI_CONSTRAINT_BLOCKED` is raised inside the scope loop, so it never
    // fires here: precedence step 2 wins and the usage catalogs `non_reaching`. Blocking
    // is a statement about executing a predicate, and there is nothing to execute.
    part def Detached {
        attribute value : Real = 5.0;
        assert constraint blocked_and_unreached {
            value == 5.0
        }
    }

    part def Live {
        attribute reading : Real = 3.0;
        assert constraint reached_gate {
            reading > 0.0
        }
    }

    part the_live : Live;
}
