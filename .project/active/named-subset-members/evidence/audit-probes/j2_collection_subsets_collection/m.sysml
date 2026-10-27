package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[4]; part hot : Server[2] :> servers; attribute total : Real = sum(servers.power); attribute hot_total : Real = sum(hot.power); }
    part rack : Rack;
}
