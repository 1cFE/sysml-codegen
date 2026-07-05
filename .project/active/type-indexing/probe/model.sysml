package ProbePkg {
    part def 'IFE Driver' {
        attr power : Real;
    }
    part def 'HIF Driver' :> 'IFE Driver' {
        attr torque : Real;
    }
    // Unrelated to 'IFE Driver' — used for the multi-owned-typing shape (Q2b).
    part def 'Other Driver' {
        attr mass : Real;
    }

    part def Facility {
        part driver : 'IFE Driver';
    }

    // Retyped usage (Q1/Q2): declared type expected last in .types; heritage
    // FeatureTyping target expected to be 'HIF Driver' only (owned, not inherited).
    part def Variant :> Facility {
        part :>> driver : 'HIF Driver';
    }

    part def Probe {
        // B2-plain (Q1): plain subtype-typed usage — .types expected to EXCLUDE
        // 'IFE Driver' (only the declared type). Baseline invariance rests on this.
        part plain_hif : 'HIF Driver';

        // Multi-owned-typing (Q2b): two unrelated user typings — expected to yield
        // two owned FeatureTyping targets, exercising most_specific's incomparable
        // branch and the V10 warning.
        part multi : 'IFE Driver', 'Other Driver';
    }
}
