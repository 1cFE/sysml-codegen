package P {
    private import ScalarValues::*;
    part def Sub { attribute x : Real default 1.0; attribute y : Real = x * 2.0; }
    part def Top { part a : Sub; }
    part def Top2 :> Top { part :>> a { :>> x = 5.0; } }
    part top : Top;
    part top2 : Top2;
}
