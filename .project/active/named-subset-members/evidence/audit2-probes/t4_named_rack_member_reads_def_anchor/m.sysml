package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Psu { attribute cap : Real default 100.0; }
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part psu : Psu; part servers : Server[2]; attribute tot : Real = sum(servers.power); }
    part def Hall { part racks : Rack[2]; attribute tot : Real = sum(racks.tot); }
    part hall : Hall {
        part rack_1 :> racks { part :>> psu { :>> cap = 50.0; } part s1 :> servers { :>> power = 20.0; attribute load : Real = power / psu.cap; attribute f : Real = power / sum(servers.power); attribute g : Real = power / sum(racks.servers.power); } }
    }
}
