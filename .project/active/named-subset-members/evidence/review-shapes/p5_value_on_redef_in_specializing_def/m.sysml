package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part def Rack12 :> Rack { part :>> servers { :>> power = 12.0; } }
    part rack : Rack12 { part server_1 :> Rack::servers; }
}
