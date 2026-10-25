package P {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost = 10.0; }
    part def Sub :> Costed { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }
    part def MidA :> Costed { part a : Sub; :>> capital_cost = a.capital_cost; }
    part def MidB :> Costed { part a : Sub { part :>> leaf[2]; } :>> capital_cost = a.capital_cost; }
    part def Top :> Costed { part x : MidA; part y : MidB; :>> capital_cost = x.capital_cost + y.capital_cost; }
    part top : Top;
}
