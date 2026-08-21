package OccurrenceCalcDomainDerivation {
    private import ScalarValues::*;

    calc def Produce {
        in attribute source : Real;
        out attribute produced : Real = source + 1.0;
    }

    calc def Consume {
        in attribute supplied : Real;
        out attribute result : Real = supplied * 3.0;
    }

    part def Cell {
        attribute source_value : Real default 5.0;

        calc first_producer : Produce {
            in source = source_value;
        }

        calc second_producer : Produce {
            in source = source_value;
        }

        calc explicit_consumer : Consume {
            in supplied = first_producer.produced;
        }
    }

    part cell : Cell[2];

    attribute package_value : Real = 7.0;

    calc package_producer : Produce {
        in source = package_value;
    }

    calc package_consumer : Consume {
        in supplied = package_producer.produced;
    }
}
