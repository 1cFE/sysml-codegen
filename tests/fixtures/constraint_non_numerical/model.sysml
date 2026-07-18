package constraint_non_numerical {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    part def MixedPurposeHost {
        attribute status : String = "on";
        attribute value : Real = 5.0;

        assert constraint status_annotation {
            status == "on"
        }

        assert constraint positive_value {
            value > 0.0
        }
    }

    part the_host : MixedPurposeHost;
}
