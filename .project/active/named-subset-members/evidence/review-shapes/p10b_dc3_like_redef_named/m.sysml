package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Rack { attribute cost : Real default 10.0; }
    part def SiteLib { part racks : Rack[*]; attribute total : Real = sum(racks.cost); }
    part def Site :> SiteLib { part :>> racks[2]; part rack_1 :> racks; part rack_2 :> racks; }
    part site : Site { part :>> rack_1 { :>> cost = 15.0; } }
}
