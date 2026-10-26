package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Psu { attribute eff : Real default 0.9; }
    part def Server { part psu : Psu; attribute e : Real = psu.eff; }
    part def Rack { part servers : Server[2]; attribute etotal : Real = sum(servers.e); }
    part rack : Rack {
        part :>> servers { part :>> psu { :>> eff = 0.5; } }
        part server_1 : Server :> servers;
    }
}
