package P {
    private import ScalarValues::*;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { attribute base : Real default 3.0; :>> capital_cost default 10.0; }
    part def Sub { part leaf : Leaf { :>> capital_cost default 15.0; } }
    part def Sub20 :> Sub { part :>> leaf { :>> capital_cost default 20.0; } }
    part def Top { part a : Sub; part c : Sub20 { part :>> leaf { :>> base = 1.0; } } }
    part top : Top;
    part def Probe { attribute p : Real default 1.0; attribute q : Real = p * 2.0; }
    part probe : Probe;
}
