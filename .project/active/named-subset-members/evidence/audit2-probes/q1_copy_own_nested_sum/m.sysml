package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Disk { attribute size : Real default 4.0; }
    part def Server { attribute power : Real default 10.0; attribute d : Real; }
    part def Rack { part servers : Server[2] { part disk : Disk; :>> d = sum(disk.size); } attribute total : Real = sum(servers.d); }
    part rack : Rack;
}
