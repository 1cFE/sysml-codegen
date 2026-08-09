package ElabMatrixC21 {
    private import ScalarValues::*;

    calc def Observe {
        in attribute x : Real;
        out attribute y : Real = x * 2.0;
    }

    part def BaseDriver {
        attribute rate : Real default 3.0;
    }

    part def SpecializedDriver :> BaseDriver {
        :>> rate = 9.0;
    }

    part def Plant {
        part driver : BaseDriver;
        calc observation : Observe { in x = driver.rate; }
    }

    part plant : Plant {
        part :>> driver : SpecializedDriver;
    }
}
