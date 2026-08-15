package CATFMFEVacuum {
    private import ScalarValues::*;

    constraint def ProductWithinBand {
        in count : Real;           // Dimensionless
        in observed : Real;        // m³/s
        in each_capacity : Real;   // m³/s
        in rel_tol : Real;         // Dimensionless
        observed >= count * each_capacity * (1.0 - rel_tol) and
        observed <= count * each_capacity * (1.0 + rel_tol)
    }

    calc def VacuumPumpAudit {
        in attribute pumping_speed_total_in : Real;  // m³/s
        in attribute pump_count : Real;              // Dimensionless
        in attribute pump_capacity : Real;           // m³/s
        out attribute sized_speed : Real = pump_count * pump_capacity;  // m³/s
    }

    part catf_vacuum_pumping {
        attribute pumping_speed_total : Real = 200.0;  // m³/s
        attribute n_pumps : Real = 48.0;                // Dimensionless
        attribute pump_capacity_each : Real = 4.17;     // m³/s

        calc pump_load : VacuumPumpAudit {
            in pumping_speed_total_in = pumping_speed_total;
            in pump_count = n_pumps;
            in pump_capacity = pump_capacity_each;
        }

        assert constraint pumping_speed_agrees : ProductWithinBand {
            in count = n_pumps;
            in observed = pumping_speed_total;
            in each_capacity = pump_capacity_each;
            in rel_tol = 0.01;
        }
    }
}
