package P {
    private import ScalarValues::*;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost default 10.0; }
    part def Sub :> Costed { part leaf : Leaf; :>> capital_cost = leaf.capital_cost * 1.0; }
    part def Top { part a : Sub; part b : Sub; }
    part def Top2 :> Top { part :>> b { :>> leaf.capital_cost = 20.0; } }
    part top : Top;
    part top2 : Top2;
}
