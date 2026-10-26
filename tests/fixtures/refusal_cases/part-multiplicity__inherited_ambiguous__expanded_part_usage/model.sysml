package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Server { attribute power : Real = 100.0; calc t : Twice { in v = power; } }
    part def Rack { part servers : Server[2]; }
    part def Rack3 :> Rack { part :>> servers[3]; }
    part def Rack4 :> Rack { part :>> servers[4]; }
    part def Mixed :> Rack3, Rack4 { part :>> Rack3::servers, Rack4::servers; }
    part rack : Mixed;
}
