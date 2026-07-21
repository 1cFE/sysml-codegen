package InstanceIndexProbe {
    private import ScalarValues::Real;

    // No calculation definitions or usages: every instance must come from part structure.
    part def ConstrainedLeaf {
        attribute reading : Real = 1.0;

        assert constraint nonnegative {
            reading >= 0.0
        }
    }

    // The assertion is inherited from ConstrainedLeaf.
    part def SpecializedLeaf :> ConstrainedLeaf;

    part def Container {
        part leaf : ConstrainedLeaf;
    }

    // Retype an inherited feature to the constrained subtype.
    part def RetypedContainer :> Container {
        part :>> leaf : SpecializedLeaf;
    }

    part def Bank {
        part member : ConstrainedLeaf [3];
    }

    part root {
        part direct_a : ConstrainedLeaf;
        part direct_b : ConstrainedLeaf;
        part container_a : Container;
        part container_b : Container;
        part specialized : RetypedContainer;
        part plain_subtype : SpecializedLeaf;
        part bank : Bank;
    }
}
