package BareSubsetBorrow {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' { :>> length = 3.0; }

        part comp_b : 'Component' {
            :>> length = 7.0;
            attribute borrowed : Real :> comp_a::length;
            attribute doubled : Real = borrowed * 2.0;
        }
    }

    part plant : 'Plant';
}
