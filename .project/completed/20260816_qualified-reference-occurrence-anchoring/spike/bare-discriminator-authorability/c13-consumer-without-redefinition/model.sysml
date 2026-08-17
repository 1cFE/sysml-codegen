package BareAliasNoConsumerRedefinition {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' { :>> length = 3.0; }

        alias a_len for comp_a::length;

        part comp_b : 'Component' {
            attribute doubled : Real = a_len * 2.0;
        }
    }

    part plant : 'Plant';
}
