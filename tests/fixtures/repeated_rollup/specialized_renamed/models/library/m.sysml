package P {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost = 10.0; }
    part def Sub :> Costed { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }
    part def Sub2 :> Sub { part :>> leaf : Leaf[2]; }
    part def Mid :> Costed { part sub : Sub[2]; :>> capital_cost = sum(sub.capital_cost); }
    part def Mid2 :> Mid { part racks2 :>> sub : Sub2[2]; }
    part def Top :> Costed { part a : Mid; part b : Mid2; :>> capital_cost = a.capital_cost + b.capital_cost; }
    part top : Top;
}
