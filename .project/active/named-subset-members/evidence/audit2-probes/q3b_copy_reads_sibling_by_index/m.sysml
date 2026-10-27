package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Disk { attribute size : Real default 4.0; }
    part def Server { attribute power : Real default 10.0; attribute o : Real; }
    part def Rack { part servers : Server[3] { part disk : Disk; :>> o = servers#(2).disk.size; } attribute total : Real = sum(servers.o); }
    part rack : Rack;
}
