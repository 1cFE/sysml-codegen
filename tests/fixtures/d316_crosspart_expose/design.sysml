package D316Design {
    private import ScalarValues::Real;
    private import D316Lib::*;

    // Package-level calc usage: visible to `consumer` by simple name, but NOT
    // one of consumer's own calc usages.
    attribute seed_src : Real = 3.0;
    calc gen : GenCalc { in seed = seed_src; }

    part consumer {
        // Single-hop cross-part EXPOSE_PURE: `gen` is a calc usage OUTSIDE this
        // part, so consumer.calc_usage_names excludes it -> the D3-16 else fires.
        attribute exposed = gen.gval;
        calc sink : SinkCalc { in inp = exposed; }
    }
}
