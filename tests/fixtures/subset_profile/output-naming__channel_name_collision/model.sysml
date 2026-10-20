package fx {
    private import ScalarValues::*;
    calc def Split { in x : Real; out 'r x' : Real = x - 1; out r_x : Real = x + 1; }
    part def Site {
        attribute v : Real = 1.0;
        calc a : Split { in x = v; }
    }
    part site : Site;
}
