package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Psu { attribute cap : Real default 100.0; }
    part def Server { attribute power : Real default 10.0; attribute load : Real; attribute fs : Real; }
    part def Rack { part psu : Psu; part servers : Server[2] { :>> load = power / psu.cap; :>> fs = power / sum(servers.power); } attribute tl : Real = sum(servers.load); attribute tf : Real = sum(servers.fs); }
    part def Hall { part racks : Rack[2]; attribute tl : Real = sum(racks.tl); attribute tf : Real = sum(racks.tf); }
    part hall : Hall;
}
