package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; part spare : Server { :>> power default 1.0; } attribute total : Real = sum(servers.power); }
    part def Hall { part racks : Rack[2]; part solo : Rack; attribute total : Real = sum(racks.total); attribute st : Real = solo.total; }
    part hall_a : Hall { part rack_1 :> racks { part :>> spare :> servers; } }
    part hall_b : Hall;
}
