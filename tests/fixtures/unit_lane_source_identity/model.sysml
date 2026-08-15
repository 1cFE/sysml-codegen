package UnitLaneSourceIdentity {
    private import ScalarValues::*;

    calc def BaseLengthCalc {
        in attribute value : Real; // cm
        out attribute result : Real = value;
    }

    calc def MetreLengthCalc {
        in attribute value : Real :>> BaseLengthCalc::value; // m
        out attribute result : Real = value;
    }

    constraint def BaseLengthGuard {
        in attribute observed : Real; // cm
        in attribute limit : Real; // cm
        observed >= limit
    }

    constraint def MetreLengthGuard {
        in attribute observed : Real :>> BaseLengthGuard::observed; // m
        in attribute limit : Real :>> BaseLengthGuard::limit; // m
        observed >= limit
    }

    part def SourceIdentityCases {
        attribute base_source : Real = 1.0; // cm
        attribute metre_source : Real = 2.0; // m
        attribute alias_source : Real = 3.0; // cm
        attribute a : Real = alias_source; // m
        attribute computed_from_alias : Real = a + 1.0;

        calc base_calc : BaseLengthCalc {
            in value = base_source;
        }

        calc redefined_calc : MetreLengthCalc {
            in value = metre_source;
        }

        calc alias_calc : MetreLengthCalc {
            in value = a;
        }

        assert constraint base_guard : BaseLengthGuard {
            in observed = base_source;
            in limit = 0.0;
        }

        assert constraint redefined_guard : MetreLengthGuard {
            in observed = metre_source;
            in limit = 0.0;
        }
    }

    part source_identity : SourceIdentityCases;
}
