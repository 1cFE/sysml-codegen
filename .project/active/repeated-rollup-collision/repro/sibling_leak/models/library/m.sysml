package P {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost default 10.0; }
    part def Sub { part leaf : Leaf[3]; }
    part def Top :> Costed { part a : Sub; part b : Sub { part :>> leaf[3] { :>> capital_cost = 20.0; } } :>> capital_cost = sum(a.leaf.capital_cost) + sum(b.leaf.capital_cost); }
    part top : Top;
}
