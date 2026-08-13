package constraint_domain_calc_def_owner {
    private import ScalarValues::*;

    // An asserted constraint owned by a `calc def`. A calculation definition has no
    // attachment capability, so this usage reaches no instance and can never be
    // evaluated -- invariant 9's structural authoring error. Elaboration must halt by
    // name (SI_CONSTRAINT_UNATTACHED), naming the usage and the missing attachment.
    calc def Sizer {
        in attribute demand : Real;
        out attribute size : Real = demand * 2.0;

        assert constraint demand_positive {
            demand > 0.0
        }
    }

    part def Rig {
        attribute demand : Real = 4.0;
        calc sizer : Sizer {
            in demand = demand;
        }
    }

    part the_rig : Rig;
}
