package P {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost default 10.0; }
    part def Sub :> Costed { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }
    part def Sub20 :> Sub { part :>> leaf[3] { :>> capital_cost = 20.0; } }
    part def Top :> Costed { part a : Sub; part b : Sub20; :>> capital_cost = a.capital_cost + b.capital_cost; }
    part top : Top;
}
