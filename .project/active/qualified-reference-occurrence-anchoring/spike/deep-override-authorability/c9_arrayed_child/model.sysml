package DeepOverrideArrayedChild {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component'[2];
    }

    part plant : 'Plant' {
        :>> comp_a.length = 43.0;
    }
}
