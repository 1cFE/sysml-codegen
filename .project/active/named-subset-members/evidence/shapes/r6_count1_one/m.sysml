package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part psu : Server; attribute total : Real = psu.power; }
    part rack : Rack { part main : Server :> psu { :>> power = 15.0; } }
}
