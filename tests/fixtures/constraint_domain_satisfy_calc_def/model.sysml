package constraint_domain_satisfy_calc_def {
    private import ScalarValues::*;

    part def Rig {
        attribute mass : Real = 4.0;
        attribute budget : Real = 10.0;
    }

    requirement def MassBudget {
        subject r : Rig;
        require constraint within {
            r.mass <= r.budget
        }
    }

    // The co-firing case the precedence rule exists to resolve: a `satisfy` whose owner
    // is a `calc def`. Step 1 (form gate) matches `out_of_scope_satisfy` and step 2
    // would match `owner_kind_unattachable`, which is invariant 9's halt. Step 1 wins,
    // so this model generates rather than halting.
    calc def Sizer {
        in attribute demand : Real;
        out attribute size : Real = demand * 2.0;

        satisfy requirement budget_met : MassBudget;
    }

    part the_rig : Rig {
        calc sizer : Sizer {
            in demand = mass;
        }
    }
}
