package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Disk { attribute size : Real default 4.0; }
    part def Server { part disk : Disk; attribute d : Real = disk.size; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.d); }
    part rack : Rack { part s1 :> servers { part :>> disk { :>> size = 7.0; } attribute alld : Real = sum(servers.disk.size); attribute mine : Real = disk.size; } }
}
