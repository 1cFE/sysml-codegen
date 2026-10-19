package fx {
    private import ScalarValues::*;
    private import NumericalFunctions::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def Caster { attribute load : Real = 1.0; }
    part def Site {
        part caster : Caster [2];
        part caster_0 : Caster;
        calc c : Twice { in x = caster_0.load; }
        attribute total : Real = sum(caster.load);
    }
    part site : Site;
}
