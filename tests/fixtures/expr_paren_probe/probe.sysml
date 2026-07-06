package ExprParenProbe {
    private import ScalarValues::Real;
    private import ScalarValues::Boolean;

    // Source-only fixture for the Item-6 real-AST regression test (D4). No
    // committed extraction_snapshot.json: a stored snapshot is text, not an AST,
    // so it cannot exercise the `.function`-bearing node that caused the dispatch
    // bug. Each output covers one helper branch shape so a C2/C3-class bug cannot
    // ship silently.
    calc def ParenProbeCalc {
        in attribute a : Real;
        in attribute b : Real;
        in attribute c : Real;
        in attribute capacity : Real;
        in attribute rate : Real;
        in attribute flag_x : Boolean;
        in attribute flag_y : Boolean;

        // Equal-precedence, associativity-unfavored repro (INV-3): (rate / 2.0)
        // is the right child of a `*` at equal precedence -> parens required.
        out attribute repro : Real = capacity * rate + capacity * (rate / 2.0) * 3.0;

        // Unequal precedence, looser child on each side (C2).
        out attribute add_left : Real = (a + b) * c;
        out attribute add_right : Real = a * (b + c);

        // Unary over binary (C3): a binary operand of a unary op wraps.
        out attribute neg_group : Real = -(a + b);
        out attribute bool_group : Boolean = not (flag_x and flag_y);

        // Power right-associativity: natural nesting flat, forced left wrapped.
        out attribute pow_flat : Real = a ** b ** c;
        out attribute pow_forced : Real = (a ** b) ** c;
    }
}
