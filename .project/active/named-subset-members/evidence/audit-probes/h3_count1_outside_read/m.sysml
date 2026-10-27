package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Psu { attribute eff : Real default 0.9; }
    part def Server { part psu : Psu; part main_psu : Psu :> psu { :>> eff = 0.5; } }
    part def Rack { part server : Server; attribute e : Real = server.psu.eff * 2.0; }
    part rack : Rack;
}
