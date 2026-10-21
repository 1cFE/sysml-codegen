package fx {
    private import ScalarValues::*;
    calc def Split { in x : Real; out lo : Real = x - 1; out hi : Real = x + 1; }
    part def Site {
        attribute a : Real = 1.0;
        calc p : Split { in x = a; }
        calc q : gx::Split { in x = a; }
    }
    part site : Site;
}
