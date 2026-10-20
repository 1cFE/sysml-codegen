package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Rack { attribute p : Real = 1.0; calc t : Twice { in v = p; } }
    part def Site { attribute n : Integer default 2; part racks : Rack[n]; }
    part tuned : Site { attribute :>> n default 3; }
}
