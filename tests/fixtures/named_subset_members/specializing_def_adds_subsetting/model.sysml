package ns {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; part spare : Server { :>> power = 1.0; } attribute total : Real = sum(servers.power); }
    part def PoolRack :> Rack { part :>> spare :> servers; }
    part rack_a : PoolRack;
    part rack_b : Rack;
}
