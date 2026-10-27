package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    private import SequenceFunctions::size;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); attribute avg : Real = sum(servers.power) / size(servers); }
    part rack : Rack { part server_1 :> servers { :>> power = 15.0; } }
}
