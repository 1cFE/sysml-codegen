package fx {
    private import ScalarValues::*;
    calc def Add { in x : Real; in y : Real; return r : Real = x + y; }
    part def Site {
        attribute 'a b' : Real = 1.0;
        attribute a_b : Real = 2.0;
        calc c : Add { in x = 'a b'; in y = a_b; }
    }
    part site : Site;
}
