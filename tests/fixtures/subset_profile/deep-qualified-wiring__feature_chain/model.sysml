package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; out attribute r : Real = 2.0 * v; }
    part def Sensor { attribute reading : Real = 1.0; calc core : Twice { in v = reading; } }
    part def Station { part sensor : Sensor; }
    calc def Shift { in d : Real; in b : Real; out attribute s : Real = d - b; }
    part def Analyzer { attribute base : Real = 0.0; }
    part system {
        part station : Station;
        part analyzer : Analyzer {
            calc consumer : Shift { in d = station.sensor.core.r; in b = base; }
        }
    }
}
