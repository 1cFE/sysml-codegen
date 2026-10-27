package s {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    part def Server { attribute power : Real default 10.0; attribute fs : Real; attribute fr : Real; }
    part def Rack { attribute total : Real; }
    part hall {
        part racks : Rack[2] {
            part servers : Server[2] { :>> fs = power / sum(servers.power); :>> fr = power / sum(racks.servers.power); }
            :>> total = sum(servers.fs);
        }
        attribute ts : Real = sum(racks.total);
        attribute tr : Real = sum(racks.servers.fr);
    }
}
