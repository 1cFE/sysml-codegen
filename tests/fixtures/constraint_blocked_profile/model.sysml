package constraint_blocked_profile {
    private import ScalarValues::*;

    // Minimal calc def so build_pipeline_context has a pipeline to build
    // (same reason as constraint_inline's Noop).
    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    // The assertion uses real-valued equality — a construct the executable
    // profile BLOCKS (block_real_equality: no invented tolerance). The wired
    // pipeline (lower_constraints_enabled=True) must halt generation with a
    // reason-grade diagnostic, end to end, not just at lower_constraints.
    part def BlockedHost {
        attribute value : Real = 5.0;
        assert constraint exact {
            value == 5.0
        }
    }

    part the_host : BlockedHost;
}
