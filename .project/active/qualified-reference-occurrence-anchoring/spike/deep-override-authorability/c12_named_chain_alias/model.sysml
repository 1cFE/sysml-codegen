package DeepOverrideNamedChainAlias {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component';
    }

    part plant : 'Plant' {
        attribute alias_length :>> comp_a.length;
        :>> alias_length = 43.0;
    }
}
