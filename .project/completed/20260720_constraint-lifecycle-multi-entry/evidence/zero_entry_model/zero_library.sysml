package zero_library {
    private import ScalarValues::*;

    calc def 'Value Calc' {
        doc /* Constant output, no `in` parameters -> not an entry channel. */
        out attribute value : Real = 2.0 * 3.0;
    }

    calc def 'Limit Calc' {
        doc /* Constant limit, no `in` parameters -> not an entry channel. */
        out attribute limit : Real = 10.0;
    }

    constraint def 'Within Limit' {
        doc /* Both operands are calc outputs, so the package has a constraint
        report but ZERO entry channels. */
        in attribute measured : Real;
        in attribute ceiling : Real;
        measured <= ceiling
    }
}
