package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; attribute x : Real; }
    part def Rack { part servers : Server[2] { :>> x = servers.power * 1.0; } attribute total : Real = sum(servers.x); }
    part rack : Rack;
}
