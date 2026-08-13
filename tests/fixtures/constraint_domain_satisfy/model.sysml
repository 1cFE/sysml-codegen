package constraint_domain_satisfy {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

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

    // `satisfy` is a SatisfyRequirementUsage, which subclasses RequirementUsage rather
    // than AssertConstraintUsage, so the pre-expansion sweep picks it up and it would
    // otherwise be indistinguishable from a bare `constraint`. It gets its own source
    // form and its own named exclusion inside the domain, never an absence.
    part the_rig : Rig {
        satisfy requirement budget_met : MassBudget by the_rig;
    }
}
