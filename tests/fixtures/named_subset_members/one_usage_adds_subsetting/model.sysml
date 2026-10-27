package ns {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; part spare : Server { :>> power default 1.0; } attribute total : Real = sum(servers.power); }
    part rack_a : Rack { part :>> spare :> servers { :>> power = 15.0; } }
    part rack_b : Rack;
}
