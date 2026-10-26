package fx {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[4]; attribute total : Real = sum(servers.power); }
    part rack : Rack { part a : Server[2] :> servers; }
}
