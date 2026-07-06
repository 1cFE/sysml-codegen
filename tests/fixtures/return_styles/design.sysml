package ReturnStylesDesign {
    private import ScalarValues::Real;
    private import ReturnStylesLibrary::*;

    // Design part binding every calc-def input, so the four styles flow through
    // backtracker -> graph -> generation (D3, full-pipeline capture). Bare `in`
    // inputs bind exactly like `in attribute` ones: `in <name> = <literal>`.
    part rs_design {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        attribute c : Real = 3.0;
        attribute d : Real = 4.0;

        calc ca : ControlA {
            in a = a;
        }

        calc cb : NamedReturnB {
            in b = b;
        }

        calc cc : BareInC {
            in x = c;
        }

        calc cd : StyleD {
            in d = d;
        }
    }
}
