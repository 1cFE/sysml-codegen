package NumericEvidence {
    private import ScalarValues::*;

    calc def Split {
        in attribute x : Real;
        out attribute twice : Real = x * 2.0;
        out attribute shifted : Real = x + 7.0;
    }

    calc def Combine {
        in attribute a : Real;
        in attribute b : Real;
        out attribute total : Real = a + b;
    }

    part plant {
        attribute source : Real = 3.0;
        calc split : Split { in x = source; }
        calc combine : Combine {
            in a = split.twice;
            in b = split.shifted;
        }
    }
}
