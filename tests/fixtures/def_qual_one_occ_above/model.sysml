package def_qual_one_occ_above {
    private import ScalarValues::*;

    // D-6, definition-owned leaf: the consumer is ABOVE the qualifying part
    // definition and exactly one occurrence exists below it. Expected: refused,
    // SI_OCCURRENCE_MISSING — descendant uniqueness cannot invent an occurrence.
    calc def Revenue {
        in attribute availability : Real;
        out attribute revenue : Real = availability * 100.0;
    }

    part def 'Plant' {
        attribute availability : Real default 0.85;
    }

    part def 'Fleet' {
        part plant_a : 'Plant' { :>> availability = 0.11; }

        calc revenue_calc : Revenue {
            in availability = 'Plant'::availability;
        }
    }

    part fleet : 'Fleet';
}
