package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Psu { attribute cap : Real default 100.0; }
    part def Server { attribute power : Real default 10.0; attribute load : Real; }
    part def Rack { }
    part hall {
        part racks : Rack[2] { part psu : Psu; part servers : Server[2] { :>> load = power / psu.cap; } }
        part rack_1 :> racks { part :>> psu { :>> cap = 50.0; } }
        attribute tl : Real = sum(racks.servers.load);
    }
}
