package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part rack : Rack {
        part :>> servers = (a, b);
        part a : Server { :>> power = 15.0; }
        part b : Server { :>> power = 20.0; }
    }
}
