package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def BigServer :> Server { attribute extra : Real default 5.0; attribute :>> power = 30.0 + extra; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part rack : Rack { part server_1 : BigServer :> servers; }
}
