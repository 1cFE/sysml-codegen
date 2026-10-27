package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; attribute frac : Real; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.frac); }
    part rack : Rack { part :>> servers[4] { :>> frac = power / sum(servers.power); } }
}
