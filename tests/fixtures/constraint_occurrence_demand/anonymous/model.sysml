package OccurrenceDemandAnonymous {
    private import ScalarValues::*;

    calc def PassThrough {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def Nonnegative {
        in attribute value : Real;
        value >= 0.0
    }

    part def Admitted {
        attribute admitted_value : Real;
        assert constraint : Nonnegative {
            in value = admitted_value;
        }
    }

    part def Excluded {
        attribute excluded_value : Real;
        constraint : Nonnegative {
            in value = excluded_value;
        }
    }

    requirement def Unsupported {
        attribute unsupported_value : Real = 97.0;
        assert constraint unsupported_check : Nonnegative {
            in value = unsupported_value;
        }
    }

    calc keep_pipeline : PassThrough {
        in x = 1.0;
    }

    part design {
        part admitted : Admitted {
            :>> admitted_value = 3.0;
        }
        part excluded : Excluded {
            :>> excluded_value = 41.0;
        }
    }
}
