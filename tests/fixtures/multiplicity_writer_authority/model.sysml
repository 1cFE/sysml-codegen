package MultiplicityWriterAuthority {
    private import ScalarValues::*;

    calc def Observe {
        in attribute value : Real;
        out attribute observed : Real = value;
    }

    part def Cell {
        attribute mass : Real default 2.0;

        calc observe_mass : Observe {
            in value = mass;
        }
    }

    part def ValidRow {
        attribute count : Integer = 2;
        part cell : Cell[count];
    }

    attribute unrelated_count : Integer = 3;

    part def UnrelatedWriterRow {
        part cell : Cell[unrelated_count];
    }

    part valid_row : ValidRow;
    part unrelated_writer_row : UnrelatedWriterRow;
}
