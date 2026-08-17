package BareAliasCalcActual {
    private import ScalarValues::*;

    calc def 'Doubler' {
        in w : Real;
        return result : Real = w * 2.0;
    }

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' { :>> length = 3.0; }

        alias a_len for comp_a::length;

        part comp_b : 'Component' {
            :>> length = 7.0;
            calc doubler : 'Doubler' { in w = a_len; }
        }
    }

    part plant : 'Plant';
}
