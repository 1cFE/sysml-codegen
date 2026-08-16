package DeepOverrideSelfDirectMember {
    private import ScalarValues::*;

    part def 'Plant' {
        attribute length : Real default 1.0;
    }

    part plant : 'Plant' {
        :>> self.length = 43.0;
    }
}
