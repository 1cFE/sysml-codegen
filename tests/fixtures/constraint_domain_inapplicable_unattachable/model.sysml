package constraint_domain_inapplicable_unattachable {
    private import ScalarValues::*;

    constraint def Positive {
        in v : Real;
        v > 0.0
    }

    // Invariant 6: marking an asserted gate inapplicable is a coverage statement and must
    // not suppress invariant 9's authoring error. This gate is owned by a `calc def`, so
    // nothing could ever attach it, and the annotation does not buy it silence.
    calc def Sizer {
        in attribute demand : Real;
        out attribute size : Real = demand * 2.0;

        assert constraint marked_but_unattachable : Positive {
            doc /* @inapplicable: marked, and still an authoring error */
            in v = demand;
        }
    }

    part def Rig {
        attribute load : Real = 4.0;
        calc sizer : Sizer {
            in demand = load;
        }
    }

    part the_rig : Rig;
}
