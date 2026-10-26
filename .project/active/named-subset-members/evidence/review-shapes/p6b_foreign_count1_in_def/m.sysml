package s {
    private import ScalarValues::*;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part psu : Server; part sub { part main :> psu { :>> power = 15.0; } } attribute total : Real = psu.power * 2.0; }
    part rack : Rack;
}
