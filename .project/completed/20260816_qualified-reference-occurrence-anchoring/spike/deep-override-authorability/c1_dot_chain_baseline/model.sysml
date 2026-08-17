package DeepOverrideDotChain {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component';
        part comp_b : 'Component';
    }

    part plant : 'Plant' {
        :>> comp_a.length = 43.0;
    }
}
