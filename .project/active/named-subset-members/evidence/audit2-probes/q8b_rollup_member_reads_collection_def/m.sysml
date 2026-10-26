package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost default 10.0; }
    part def Sub :> Costed { part leaf : Leaf[3]; part l1 :> leaf { :>> capital_cost default 40.0; attribute share : Real = capital_cost / sum(leaf.capital_cost); } :>> capital_cost = sum(leaf.capital_cost); }
    part def Top :> Costed { part a : Sub; part b : Sub; part c : Sub { part :>> l1 { :>> capital_cost = 20.0; } } :>> capital_cost = a.capital_cost + b.capital_cost + c.capital_cost; }
    part top : Top;
}
