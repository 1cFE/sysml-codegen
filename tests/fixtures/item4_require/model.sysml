package item4_require {
    private import ScalarValues::*;

    // Item-4-owned fixture (PIPELINE-TRUTH). Live-only (no snapshot): it pins
    // the `require constraint` shape as a reported plain ConstraintUsage, and a
    // requirement usage as a swept-and-EXCLUDED RequirementUsage — the only
    // codegen fixture that exercises the exclusion / sentinel path live.

    part def Widget {
        attribute cost : Real;
        attribute budget : Real;
    }

    requirement def BudgetReq {
        subject w : Widget;

        // `require constraint` is a plain ConstraintUsage reached through a
        // RequirementConstraintMembership — a dropped predicate, kind PLAIN.
        require constraint within_budget {
            w.cost <= w.budget
        }
    }

    part demo : Widget;

    // A requirement usage: RequirementUsage <: ConstraintUsage, so the
    // subtype-aware sweep picks it up and the RequirementUsage exclusion drops
    // it (kind REQUIREMENT, excluded — not a dropped predicate).
    requirement demo_req : BudgetReq {
        subject demo;
    }
}
