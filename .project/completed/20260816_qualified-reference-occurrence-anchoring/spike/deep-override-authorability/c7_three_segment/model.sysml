package DeepOverrideThreeSegment {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Assembly' {
        part comp_a : 'Component';
    }

    part def 'Plant' {
        part asm : 'Assembly';
    }

    part plant : 'Plant' {
        :>> asm.comp_a.length = 43.0;
    }
}
