package DeepOverrideAnonLeaf {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' {
            :>> length = 3.0;
        }
        part comp_b : 'Component';
    }

    part plant : 'Plant' {
        :>> comp_a.length = 43.0;
    }
}
