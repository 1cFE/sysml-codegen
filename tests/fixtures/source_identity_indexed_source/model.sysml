package source_identity_indexed_source {
    private import ScalarValues::*;

    // SOURCE-IDENTITY Item 4 readiness fixture (see PROVENANCE.md).
    // Realizes SRC-02/02a: a valid KerML #(i) indexed value expression used
    // where source feature identity is required. Valid SysML, outside the
    // executable subset — extraction must retain the indexed form as evidence
    // and never silently flatten the index segment away.

    calc def 'Twice Calc' {
        in attribute r_in : Real;
        out attribute y : Real = r_in * 2.0;
    }

    calc def 'Thrice Calc' {
        in attribute r_in : Real;
        out attribute z : Real = r_in * 3.0;
    }

    part def 'Probe Plant' {
        attribute plant_r : Real = 3.0;
    }

    part def 'Design Ctx' {
        part plants : 'Probe Plant'[2];

        calc c1 : 'Twice Calc' {
            in r_in = plants#(1).plant_r;
        }
        calc c2 : 'Thrice Calc' {
            in r_in = plants#(2).plant_r;
        }
    }

    part design_ctx : 'Design Ctx';
}
