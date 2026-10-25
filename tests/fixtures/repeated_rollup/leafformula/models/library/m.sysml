package P {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { attribute a : Real = 2.0; :>> capital_cost = a * 5.0; }
    part def Sub :> Costed { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }
    part top : Sub;
}
