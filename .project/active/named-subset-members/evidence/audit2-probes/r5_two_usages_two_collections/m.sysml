package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; part backups : Server[2]; part spare : Server { :>> power default 1.0; } attribute total : Real = sum(servers.power); attribute tb : Real = sum(backups.power); }
    part rack_a : Rack { part :>> spare :> servers; }
    part rack_b : Rack { part :>> spare :> backups; }
}
