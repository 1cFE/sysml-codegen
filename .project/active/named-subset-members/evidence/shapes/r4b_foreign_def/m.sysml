package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part def Hall { part rack : Rack; part spare : Server :> Rack::servers; }
    part hall : Hall;
}
