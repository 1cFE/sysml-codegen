package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Sub { attribute power : Real default 1.0; }
    part def Server { attribute power : Real default 10.0; part servers : Sub[2]; attribute inner : Real = sum(servers.power); }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); attribute ti : Real = sum(servers.inner); }
    part rack : Rack { part server_1 :> servers { :>> power = 15.0; attribute seen : Real = sum(servers.power); } }
}
