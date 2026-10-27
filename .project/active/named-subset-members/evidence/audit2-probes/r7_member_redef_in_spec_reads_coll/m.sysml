package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; attribute frac : Real; }
    part def Rack { part servers : Server[2]; part spare : Server { :>> power default 30.0; } attribute total : Real = sum(servers.power); }
    part def PoolRack :> Rack { part :>> spare :> servers { :>> frac = power / sum(servers.power); } }
    part rack_a : PoolRack;
    part rack_b : Rack;
    attribute fa : Real = rack_a.spare.frac;
}
