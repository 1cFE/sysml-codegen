package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Psu { attribute eff : Real default 0.9; }
    part def Server { part psu : Psu; attribute e : Real = psu.eff * 2.0; }
    part server : Server { part main_psu : Psu :> psu { :>> eff = 0.5; } }
}
