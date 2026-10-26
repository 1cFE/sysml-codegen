package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; part spare : Server { :>> power default 1.0; } attribute total : Real = sum(servers.power); }
    part def Hall { part racks : Rack[2]; attribute total : Real = sum(racks.total); }
    part def PoolHall :> Hall { part :>> racks { part :>> spare :> servers; } }
    part hall_a : PoolHall;
    part hall_b : Hall;
}
