package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; }
    part def Hall { part rack : Rack { part server_1 :> servers { :>> power = 15.0; } } attribute total : Real = sum(rack.servers.power); }
    part hall : Hall;
}
