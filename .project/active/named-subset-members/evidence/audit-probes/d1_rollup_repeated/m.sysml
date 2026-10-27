package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[2]; attribute total : Real = sum(servers.power); }
    part def Hall { part racks : Rack[3]; attribute total : Real = sum(racks.total); }
    part hall : Hall {
        part rack_1 :> racks { part server_1 :> servers { :>> power = 15.0; } }
        part rack_2 :> racks { part server_1 :> servers { :>> power = 20.0; } part server_2 :> servers { :>> power = 30.0; } }
    }
}
