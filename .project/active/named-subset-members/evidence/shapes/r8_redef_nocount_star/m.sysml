package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[*]; attribute total : Real = sum(servers.power); }
    part rack : Rack { part :>> servers { :>> power = 15.0; } }
}
