package OccurrenceDomainDerivation {
    private import ScalarValues::*;

    calc def Scale {
        in attribute x : Real;
        out attribute y : Real = x * 2.0;
    }

    attribute package_source : Real = 2.0;

    calc package_scale : Scale {
        in x = package_source;
    }

    part def Sensor {
        attribute reading : Real default 3.0;

        calc scale_reading : Scale {
            in x = reading;
        }
    }

    part def SpecialSensor :> Sensor {
        attribute :>> reading = 4.0;
    }

    part def Container {
        part sensor : Sensor;

        calc explicit_sensor_reading : Scale {
            in x = sensor.reading;
        }
    }

    part def VariantContainer :> Container {
        part :>> sensor : SpecialSensor;
    }

    part direct_container : Container;
    part repeated_container : Container[2];
    part variant_container : VariantContainer;

    part package_nested {
        part nested_sensor : Sensor;
    }

    calc explicit_nested_reader : Scale {
        in x = package_nested.nested_sensor.reading;
    }

    calc definition_only_reader : Scale {
        in x = Sensor::reading;
    }
}
