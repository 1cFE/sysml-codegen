package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part psu : Server; attribute total : Real = sum(psu.power); }
    part rack : Rack { part a : Server :> psu; part b : Server :> psu; }
}
