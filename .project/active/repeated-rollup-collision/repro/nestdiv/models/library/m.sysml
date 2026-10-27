package P {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost = 10.0; }
    part def Sub :> Costed { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }
    part def Row :> Costed { part a : Sub; part b : Sub { part :>> leaf[2]; } :>> capital_cost = a.capital_cost + b.capital_cost; }
    part def Top :> Costed { part row : Row[2]; :>> capital_cost = sum(row.capital_cost); }
    part top : Top;
}
