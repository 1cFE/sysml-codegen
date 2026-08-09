package ElabMatrixC14 {
    private import ScalarValues::*;

    calc def RenamedA { in attribute first_input : Real; out attribute y : Real = first_input; }
    calc def RenamedB { in attribute second_input : Real; out attribute y : Real = second_input; }
    part def Source { attribute value : Real = 9.0; }

    part def Host {
        part source : Source;
        calc first_calc : RenamedA { in first_input = source.value; }
        calc second : RenamedB { in second_input = source.value; }
    }

    part host : Host;
}
