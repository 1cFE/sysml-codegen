package DeepOverrideInlineDef {
    private import ScalarValues::*;

    part def 'Plant' {
        part comp_a {
            attribute length : Real = 1.0;
        }
    }

    part plant : 'Plant' {
        :>> comp_a.length = 43.0;
    }
}
