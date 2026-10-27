package P {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost = 10.0; }
    part def Sub :> Costed { part leaf : Leaf[3]; attribute sub_total : Real = sum(leaf.capital_cost); :>> capital_cost = sub_total; }
    part def Top :> Costed { part sub : Sub[2]; :>> capital_cost = sum(sub.capital_cost); }
    part top : Top;
}
