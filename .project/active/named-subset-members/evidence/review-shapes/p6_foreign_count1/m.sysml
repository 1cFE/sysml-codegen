package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part main_server : Server;
    part def Site { part mine :> main_server { :>> power = 15.0; } }
    part site : Site;
    attribute total : Real = main_server.power * 2.0;
}
