package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; part spares : Server[1]; attribute total : Real = sum(servers.power) + sum(spares.power); }
    part rack : Rack { part server_1 : Server :> servers { :>> power = 15.0; } part spare_1 : Server :> spares { :>> power = 1.0; } }
}
