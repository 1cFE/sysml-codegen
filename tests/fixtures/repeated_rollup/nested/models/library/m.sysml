package P {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { :>> capital_cost = 10.0; }
    part def Rack :> Costed { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }
    part def Row :> Costed { part rack : Rack[2]; :>> capital_cost = sum(rack.capital_cost); }
    part def Hall :> Costed { part row : Row[2]; :>> capital_cost = sum(row.capital_cost); }
    part hall : Hall;
}
