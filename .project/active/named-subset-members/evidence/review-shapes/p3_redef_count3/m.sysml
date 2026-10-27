package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part def Rack3 :> Rack { part :>> servers[3]; }
    part rack : Rack3 { part server_1 :> servers { :>> power = 15.0; } }
}
