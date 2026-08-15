package ElabMatrixC5 {
    private import ScalarValues::*;

    calc def Observe {
        in attribute x : Real;
        out attribute y : Real = x * 2.0;
    }

    part def Analyzer {
        attribute baseline : Real default 3.0;
    }

    part measurement_system {
        part analyzer : Analyzer {
            :>> baseline = 12.7;
            calc observation : Observe {
                in x = analyzer::baseline;
            }
        }
    }
}
