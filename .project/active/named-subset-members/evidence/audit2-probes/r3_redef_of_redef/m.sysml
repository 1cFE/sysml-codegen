package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; part spare : Server { :>> power default 1.0; } attribute total : Real = sum(servers.power); }
    part def PoolRack :> Rack { part :>> spare :> servers; }
    part def P2 :> PoolRack { part :>> spare { :>> power = 3.0; } }
    part rack_a : P2;
    part rack_c : Rack;
    part rack_d : PoolRack;
}
