package BareSubsetSiblingUsage {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' { :>> length = 3.0; }

        part comp_b : 'Component' :> comp_a {
            attribute doubled : Real = length * 2.0;
        }
    }

    part plant : 'Plant';
}
