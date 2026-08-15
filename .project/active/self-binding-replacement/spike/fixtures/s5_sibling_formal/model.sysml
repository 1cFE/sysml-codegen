package S5SiblingFormal {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — the D-5 rename applied to a calc def that ALREADY declares a
    // member named like the part attribute. The formal is renamed (`availability_in`),
    // so the binding is NOT a self-binding; but the bare RHS `availability` now
    // shadows onto the calc's own OUT parameter instead of the part attribute.
    // The part attribute's 0.85 must never reach the calculation if that happens.
    calc def Revenue {
        in attribute availability_in : Real;
        out attribute availability : Real = availability_in * 100.0;
    }

    part def 'Plant' {
        attribute availability : Real = 0.85;

        calc revenue_calc : Revenue {
            in availability_in = availability;
        }
    }

    part plant : 'Plant';
}
