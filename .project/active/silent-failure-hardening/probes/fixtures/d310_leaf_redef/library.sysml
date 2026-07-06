// D3-10: two PartDefs named `Motor` in different packages, each with a LITERAL
// `:>> power` redefinition of a DIFFERENT value. `_find_literal_redefinition`'s
// name-based fallback (graph_builder ~1349) matches by the last `__` segment of
// owning_part_qn ("Motor") plus attribute_name ("power"), first-wins across ALL
// partdefs — so it can return the wrong PartDef's literal, silently.
package D310Base {
    private import ScalarValues::*;
    abstract part def 'Powered' {
        attribute power : Real;
    }
}

package D310PkgA {
    private import ScalarValues::*;
    private import D310Base::*;
    part def Motor :> 'Powered' {
        :>> power = 100.0;
    }
}

package D310PkgB {
    private import ScalarValues::*;
    private import D310Base::*;
    part def Motor :> 'Powered' {
        :>> power = 999.0;
    }
}

// Minimal calc def so build_pipeline_context accepts the model (probe-runnability
// gate). Isolated from the two Motor LITERAL redefinitions D3-10 exercises.
package D310Probe {
    private import ScalarValues::*;
    calc def NoopCalc {
        in attribute x : Real;
        out attribute result : Real = x;
    }
}
