package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Psu { attribute eff : Real default 0.9; }
    part def Server { part psus : Psu[2]; attribute e : Real = sum(psus.eff); }
    part def Rack { part servers : Server[2]; attribute etotal : Real = sum(servers.e); }
    part rack : Rack { part server_1 : Server :> servers { part psu_a : Psu :> psus { :>> eff = 0.5; } } }
}
