package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Rack { attribute power : Real default 10.0; }
    part def ItSystem { part racks : Rack[*]; attribute total : Real = sum(racks.power); }
    part def Facility { part it_system : ItSystem; }
    part def MyFacility :> Facility {
        part :>> it_system {
            part :>> racks[2];
            part rack_1 : Rack :> racks { :>> power = 15.0; }
            part rack_2 : Rack :> racks { :>> power = 20.0; }
        }
    }
    part site { part facility : MyFacility; }
}
