package GateBSep {
    private import ScalarValues::*;

    // =====================================================================
    // Gate B probe 3b — the SECOND collision vector: the `__` separator.
    //
    // A fallback key is `{calc_eqn}__{formal}`; a design-attribute QN is
    // `{owner_path}__{name}`. Both join with `__`, and `__` is legal INSIDE a
    // SysML name. So, with no duplicate names anywhere:
    //
    //   calc usage `scaler` on `the_host`, self-named binding `in gain = gain`
    //     -> lenient terminal miss -> fallback key GateBSep__the_host__scaler__gain
    //        (the self-named step-limit shape; cf. tests/fixtures/shared_producer)
    //   attribute named `scaler__gain` on `the_host`, VALUELESS
    //     -> design-attribute QN     GateBSep__the_host__scaler__gain
    //
    // Same string. The attribute is valueless (V11's second leg) and a
    // self-named constraint actual makes the APPENDED constraint module wire
    // that exact key -- probe 1's shape B, reached from a real model.
    //
    // NOT a test fixture. Probe scratch; lives with the work item.
    // =====================================================================

    constraint def 'Nonneg' {
        in attribute v : Real;

        v >= 0.0
    }

    calc def Scaler {
        in attribute gain : Real;
        out attribute scaled : Real = gain * 2.0;
    }

    part def Host;

    part the_host : Host {
        attribute gain : Real = 40.0;

        // valueless design attribute whose NAME carries the separator
        attribute scaler__gain : Real;

        calc scaler : Scaler {
            in gain = gain;
        }

        assert constraint nonneg : 'Nonneg' {
            in v = scaler__gain;
        }
    }
}
