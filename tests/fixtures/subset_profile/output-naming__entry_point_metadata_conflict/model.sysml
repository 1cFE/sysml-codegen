package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    calc def TwiceI { in x : Integer; return r : Integer = x * 2; }
    part def Site {
        attribute n : Integer = 2;
        calc c1 : Twice { in x = n; }
        calc c2 : TwiceI { in x = n; }
    }
    part site : Site;
}
