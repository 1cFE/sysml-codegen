package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { attribute n : Natural default 3; part servers : Server[n]; attribute total : Real = sum(servers.power); }
    part def Rack2 :> Rack { attribute :>> n default 2; part :>> servers; }
    part rack : Rack2 { part server_1 :> servers { :>> power = 15.0; } }
}
