package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; attribute frac : Real default 0.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.frac); }
    part rack : Rack {
        part server_1 : Server :> servers { :>> power = 30.0; :>> frac = power / sum(servers.power); }
        part server_2 : Server :> servers { :>> frac = power / sum(servers.power); }
    }
}
