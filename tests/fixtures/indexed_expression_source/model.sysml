package IndexedExpressionSource {
    private import ScalarValues::*;

    calc def Twice {
        in attribute source : Real;
        out attribute result : Real = source * 2.0;
    }

    part def Cell {
        attribute mass : Real default 3.0;
    }

    part def Array {
        part cells : Cell[3];

        calc indexed_observer : Twice {
            in source = cells#(2).mass;
        }
    }

    part array : Array;
}
