package fx {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part rack : Rack { part :>> servers; }
    part def Hall { part spare : Server :> rack::servers { attribute :>> power = 15.0; } }
    part hall : Hall;
}
