package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost default 10.0; attribute share : Real; }
    part def Sub :> Costed { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }
    part def Top :> Costed {
        part a : Sub { part l1 :> leaf { :>> capital_cost = 40.0; :>> share = capital_cost / sum(leaf.capital_cost); } }
        part b : Sub;
        :>> capital_cost = a.capital_cost + b.capital_cost;
    }
    part top : Top;
}
