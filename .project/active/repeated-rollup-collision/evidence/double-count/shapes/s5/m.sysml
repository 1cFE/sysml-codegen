package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; }
    part def Rack { part servers : Server[*]; attribute total : Real = sum(servers.power); }
    part def ItSystem { part racks : Rack[*]; }
    part def Facility { part it_system : ItSystem; }
    part def MyFacility :> Facility {
        part :>> it_system {
            part :>> racks[2] { part :>> servers[0]; }
            part rack_1 : Rack :> racks {
                part server_1 : Server { :>> power = 15.0; }
                part server_2 : Server { :>> power = 20.0; }
            }
            part rack_2 : Rack :> racks {
                part server_1 : Server { :>> power = 15.0; }
                part server_2 : Server { :>> power = 20.0; }
            }
        }
    }
    part site { part facility : MyFacility; }
}
