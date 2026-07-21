package zero_plant {
    private import ScalarValues::*;
    private import zero_library::*;

    part def 'Zero Plant' {
        doc /* A constraint-bearing package with zero entry channels: every
        constraint operand is produced by an internal calc, so nothing becomes
        an entry-point parameter. */
        calc value_calc : 'Value Calc' {}
        calc limit_calc : 'Limit Calc' {}

        assert constraint within : 'Within Limit' {
            in measured = value_calc.value;
            in ceiling = limit_calc.limit;
        }
    }

    part zeroPlant : 'Zero Plant';
}
