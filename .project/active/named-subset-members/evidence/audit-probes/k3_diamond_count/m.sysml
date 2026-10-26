package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def A { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part def B :> A { part :>> servers; }
    part def C :> A { part :>> servers; }
    part def D :> B, C { part :>> B::servers, C::servers; }
    part d : D;
}
