package NamespaceDistinguishabilityProbe {
    private import ScalarValues::Real;

    calc def Echo {
        in attribute value : Real;
        out attribute echoed : Real = value;
    }

    part def Sensor {
        attribute reading : Real default = 1.0;

        calc core : Echo {
            in value = reading;
        }
    }

    part def Array {
        part sensor : Sensor;
    }

    part def Station {
        part array : Array;
    }

    part station : Station {
        part array : Array {
            part sensor : Sensor;
        }
    }
}
