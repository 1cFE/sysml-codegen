package P {
    private import ScalarValues::*;
    abstract part def Costed { attribute capital_cost : Real; }
    part def Leaf :> Costed { attribute base : Real default 3.0; :>> capital_cost default 10.0; }
    part def Sub :> Costed { part leaf : Leaf; :>> capital_cost = leaf.capital_cost * 1.0; }
    part def Top {
        part a : Sub;
        part b : Sub {
            part :>> leaf {
                attribute x : Real = base * 2.0;
                assert constraint cap { capital_cost <= 15.0 }
            }
        }
    }
    part top : Top;
}
