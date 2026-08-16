package sibling_formal_cycle {
    private import ScalarValues::*;

    // The D-5 rename residual risk: the calc def ALREADY declares an out member
    // named like the part attribute. The formal is renamed (`availability_in`),
    // so the binding is NOT a self-binding; but the bare RHS `availability`
    // shadows onto the calc's own OUT parameter instead of the part attribute.
    // The input then consumes the calc's own output — a typed producer
    // dependency cycle, refused by graph validation. The part attribute's 0.85
    // must never reach the calculation if that happens.
    calc def Revenue {
        in attribute availability_in : Real;
        out attribute availability : Real = availability_in * 100.0;
    }

    part def Plant {
        attribute availability : Real = 0.85;

        calc revenue_calc : Revenue {
            in availability_in = availability;
        }
    }

    part plant : Plant;
}
