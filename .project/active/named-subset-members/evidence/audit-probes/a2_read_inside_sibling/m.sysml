package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part def Mon { attribute seen : Real; }
    part rack : Rack {
        part server_1 : Server :> servers { :>> power = 15.0; }
        part mon : Mon { :>> seen = sum(servers.power); }
    }
}
