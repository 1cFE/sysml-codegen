package UsageOwnedReferenceConsumers {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;

    calc def AreaCalculation {
        in attribute length_in : Real;
        out attribute area : Real = length_in * 2.0;
    }

    constraint def 'Length Bound' {
        in attribute length_in : Real;
        length_in < 100.0
    }

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' { :>> length = 3.0; }

        part comp_b : 'Component' {
            :>> length = 7.0;

            attribute aliased_length : Real = comp_a::length;

            attribute doubled_length : Real = comp_a::length * 2.0;

            attribute summed_length : Real = sum(comp_a::length);

            calc area_calc : AreaCalculation {
                in length_in = comp_a::length;
            }

            calc alias_calc : AreaCalculation {
                in length_in = aliased_length;
            }

            assert constraint bound_check : 'Length Bound' {
                in length_in = comp_a::length;
            }

            assert constraint inline_check {
                comp_a::length > 0.0
            }
        }
    }

    part plant : 'Plant';
}
