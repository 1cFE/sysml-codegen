package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; part spare : Server { :>> power default 1.0; } attribute total : Real = sum(servers.power); }
    part def PoolRack :> Rack { part :>> spare :> servers; }
    part rack_x : PoolRack { part :>> spare { :>> power = 2.0; } }
    part rack_y : Rack { part :>> spare { :>> power = 2.0; } }
}
