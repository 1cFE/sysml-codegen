package DeepOverrideAttrRoot {
    private import ScalarValues::*;

    attribute def 'Dimensions' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        attribute dims : 'Dimensions';
    }

    part plant : 'Plant' {
        :>> dims.length = 43.0;
    }
}
