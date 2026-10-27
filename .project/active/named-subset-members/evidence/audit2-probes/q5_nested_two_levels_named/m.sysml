package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part def Hall { part racks : Rack[2]; attribute total : Real = sum(racks.total); }
    part hall : Hall {
        part rack_1 :> racks {
            part server_1 :> servers { :>> power = 30.0; attribute fs : Real = power / sum(servers.power); attribute fh : Real = power / sum(racks.servers.power); attribute fh2 : Real = power / sum(racks.total); }
        }
    }
}
