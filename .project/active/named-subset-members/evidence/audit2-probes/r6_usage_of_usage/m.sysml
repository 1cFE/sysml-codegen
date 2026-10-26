package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; part spare : Server { :>> power default 1.0; } attribute total : Real = sum(servers.power); }
    part def Hall { part rack_a : Rack { part :>> spare :> servers; } part rack_b : Rack; attribute ta : Real = rack_a.total; attribute tb : Real = rack_b.total; }
    part hall_1 : Hall;
    part hall_2 : Hall { part :>> rack_b { part :>> spare :> servers { :>> power = 5.0; } } }
}
