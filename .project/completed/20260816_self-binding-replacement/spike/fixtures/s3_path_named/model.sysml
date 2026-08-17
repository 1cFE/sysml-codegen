package S3PathNamed {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — shape 3 (D-7), path-named `in driver_cost = driver.cost`.
    calc def DriverCost {
        in attribute driver_cost : Real;
        out attribute total_cost : Real = driver_cost * 3.0;
    }

    part def 'Driver' {
        attribute cost : Real = 12.5;
    }

    part def 'Plant' {
        part driver : 'Driver';

        calc cost_calc : DriverCost {
            in driver_cost = driver.cost;
        }
    }

    part plant : 'Plant';
}
