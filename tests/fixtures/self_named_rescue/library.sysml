package RescueLib {
    private import ScalarValues::*;

    // Upstream producer calc: computes `throughput` from a raw input. Its output is
    // the channel the self-named binding below must rescue to.
    calc def SourceCalc {
        doc /*
        Upstream producer for the mechanism-D self-named RESCUE (SC-4, the positive
        companion to self_named_binding_trap). Its output `throughput` is a real
        channel, so the downstream `in throughput = throughput` has a RESOLVABLE
        upstream — unlike the trap, whose shared name dead-ends on the calc's own
        parameter.
        **Source**: authored fixture (Item 10, UPSTREAM-FINDINGS stage (b))
        **Reference**: spec.md SC-4 (mechanism-D rescue, positive)
        **Last Updated**: 2026-07-05
        */
        in attribute raw : Real;
        out attribute throughput : Real = raw * 1.5;
    }

    // Consumer calc whose input is named identically to the upstream channel and to
    // the part attribute that exposes it — the self-named-binding ambiguity.
    calc def SinkCalc {
        in attribute throughput : Real;
        out attribute result : Real = throughput * 2.0;
    }

    part def 'Rescue Plant' {
        doc /*
        Minimal part exercising exactly the mechanism-D self-named binding WITH a
        resolvable upstream, so the rewrite has a real channel to rescue to. Mirrors
        self_named_binding_trap structurally; the only difference is that `throughput`
        is produced upstream (source_calc.throughput) rather than dead-ending.
        **Source**: authored fixture (Item 10 stage (b))
        **Reference**: spec.md SC-4 (isolation rationale, positive companion)
        **Last Updated**: 2026-07-05
        */
        attribute raw_flow : Real = 4.0;

        // Upstream producer: source_calc.throughput is a real, wired channel.
        calc source_calc : SourceCalc {
            in raw = raw_flow;
        }

        // Expose the upstream output as a part attribute named `throughput`. This
        // gives the self-named binding below a resolvable upstream in scope.
        attribute throughput : Real = source_calc.throughput;

        // Self-named binding (mechanism D): the RHS `throughput` shares the calc
        // param's name AND the exposed attribute's name. The Item-10 rewrite must
        // redirect it to the upstream `throughput` channel (source_calc.throughput),
        // NOT bind to sink_calc's own input parameter (the trap failure mode).
        calc sink_calc : SinkCalc {
            in throughput = throughput;
        }
    }
}
