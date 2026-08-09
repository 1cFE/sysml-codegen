package ElabFiniteExpressionMultiplicity {
    private import ScalarValues::*;

    calc def Observe {
        in attribute value : Real;
        out attribute result : Real = value;
    }

    part def Cell {
        attribute value : Real default 3.0;
        calc observation : Observe {
            in value = value;
        }
    }

    part host {
        attribute count : Integer = 2 * 2;
        part cell : Cell[count];
    }
}
