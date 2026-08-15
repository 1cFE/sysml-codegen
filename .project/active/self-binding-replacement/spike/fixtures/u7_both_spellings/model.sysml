package U7BothSpellings {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — F-7 probe fixture. Both usage-qualified spellings authored as
    // real bindings in ONE model, from a symmetric position (neither is the consumer's
    // enclosing occurrence), plus the dot-path spelling for the same value, so the
    // SysIDE referents can be compared side by side.
    //
    // This fixture exists to be READ at the SysIDE layer, not to generate. Elaboration
    // is expected to refuse it; that is fine and is not what it measures.
    calc def TwoLengths {
        in attribute a_len : Real;
        in attribute b_len : Real;
        out attribute total : Real = a_len + b_len;
    }

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' { :>> length = 3.0; }
        part comp_b : 'Component' { :>> length = 7.0; }

        calc pair_calc : TwoLengths {
            in a_len = comp_a::length;   // qualified-name spelling, comp_a
            in b_len = comp_b::length;   // qualified-name spelling, comp_b
        }

        calc dot_calc : TwoLengths {
            in a_len = comp_a.length;    // feature-chain spelling, same two values
            in b_len = comp_b.length;
        }
    }

    part plant : 'Plant';
}
