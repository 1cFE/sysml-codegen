package P {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost = 10.0; }
    part def Sub :> Costed { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }
    part def Top :> Costed { part a : Sub; attribute extra : Real = 5.0; :>> capital_cost = a.capital_cost + extra; }
    part top : Top;
}
