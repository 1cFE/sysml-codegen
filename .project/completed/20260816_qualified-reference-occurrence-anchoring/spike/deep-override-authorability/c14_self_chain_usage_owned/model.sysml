package DeepOverrideSelfChainUsageOwned {
    private import ScalarValues::*;

    part def 'Plant' {
        part comp_a {
            attribute length : Real = 1.0;
        }
    }

    part plant : 'Plant' {
        part :>> comp_a {
            :>> self.length = 43.0;
        }
    }
}
