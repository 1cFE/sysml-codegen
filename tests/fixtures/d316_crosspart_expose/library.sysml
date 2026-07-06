package D316Lib {
    private import ScalarValues::Real;
    calc def GenCalc {
        in attribute seed : Real;
        out attribute gval : Real = seed * 2.0;
    }
    calc def SinkCalc {
        in attribute inp : Real;
        out attribute sout : Real = inp;
    }
}
