package constraint_domain_containment {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    // `Typed` IS typed by a part usage (`Parent::child`), so the companion's
    // structural trigger stays silent, but `Parent` is never instantiated so the
    // occurrence index yields nothing. Codegen must still grade the gate
    // `owner_has_no_occurrences`. This is invariant 9's containment direction: the
    // companion's trigger set is a strict subset of codegen's vacuous set.
    part def Typed {
        attribute value : Real = 5.0;
        assert constraint nested_vacuous_gate {
            value > 0.0
        }
    }

    part def Parent {
        part child : Typed;
    }

    part def Live {
        attribute reading : Real = 3.0;
        assert constraint reached_gate {
            reading > 0.0
        }
    }

    part the_live : Live;
}
