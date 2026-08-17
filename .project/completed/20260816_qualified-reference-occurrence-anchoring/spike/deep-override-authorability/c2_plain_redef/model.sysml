package DeepOverridePlainRedef {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component';
    }

    part plant : 'Plant' {
        part :>> comp_a : 'Component' {
            :>> length = 43.0;
        }
    }
}
