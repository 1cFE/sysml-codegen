package DeepOverrideUnresolvedLeaf {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component';
    }

    part plant : 'Plant' {
        :>> comp_a.no_such_member = 43.0;
    }
}
