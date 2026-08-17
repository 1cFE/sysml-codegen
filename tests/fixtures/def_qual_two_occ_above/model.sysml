package def_qual_two_occ_above {
    private import ScalarValues::*;

    // D-6, definition-owned leaf: the owner-qualified reference is authored
    // ABOVE the qualifying part definition, in an enclosing part that owns TWO
    // occurrences of it. Expected: refused, SI_OCCURRENCE_AMBIGUOUS — the
    // consumer sits outside every occurrence and more than one is reachable.
    calc def Revenue {
        in attribute availability : Real;
        out attribute revenue : Real = availability * 100.0;
    }

    part def 'Plant' {
        attribute availability : Real default 0.85;
    }

    part def 'Fleet' {
        part plant_a : 'Plant' { :>> availability = 0.11; }
        part plant_b : 'Plant' { :>> availability = 0.99; }

        calc revenue_calc : Revenue {
            in availability = 'Plant'::availability;
        }
    }

    part fleet : 'Fleet';
}
