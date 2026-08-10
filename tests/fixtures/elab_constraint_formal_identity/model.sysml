package ConstraintFormalIdentity {
    private import ScalarValues::*;

    constraint def 'Maximum Power' {
        in attribute 'max power' : Real;
        'max power' <= 10.0
    }

    part def Host {
        attribute reading : Real = 5.0;

        assert constraint check : 'Maximum Power' {
            in 'max power' = reading;
        }
    }

    part host : Host;
}
