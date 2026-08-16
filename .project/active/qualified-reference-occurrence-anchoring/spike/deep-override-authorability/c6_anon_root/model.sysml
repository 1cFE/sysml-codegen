package DeepOverrideAnonRoot {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component';
        part comp_b : 'Component';
    }

    part def 'Site' {
        part plant : 'Plant';
    }

    part site : 'Site' {
        :>> plant {
            :>> comp_a.length = 43.0;
        }
    }
}
