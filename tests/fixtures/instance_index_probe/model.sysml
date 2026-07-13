package InstanceIndexProbe {
    private import ScalarValues::Real;
    private import ScalarValues::Integer;

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

    // --- Item 4 extensions below. Disjoint type families from ConstrainedLeaf /
    // SpecializedLeaf so the 9-oracle above is untouched (design.md Validation #2/#3/#7/#8).

    // Collision: two definitions own a same-named member with different counts.
    part def CollisionLeaf;
    part def BankA {
        part member : CollisionLeaf [3];
    }
    part def BankB {
        part member : CollisionLeaf [2];
    }
    part bank_a : BankA;
    part bank_b : BankB;

    // [3..3] admit (C2): equal literal bounds expand to a fixed count of 3.
    part def Leaf33;
    part def Bank33 {
        part m33 : Leaf33 [3..3];
    }
    part b33 : Bank33;

    // Cartesian expansion: a fixed [2] container of a fixed [3] leaf expands to 6.
    part def CartLeaf;
    part def Inner {
        part leaf : CartLeaf [3];
    }
    part def Outer {
        part c : Inner [2];
    }
    part outer : Outer;

    // Closure x multiplicity: the query type is reached only via subtype closure,
    // and the reaching member itself has a fixed multiplicity.
    part def ClosureBase;
    part def ClosureSub :> ClosureBase;
    part def ClosureHost {
        part cs : ClosureSub [2];
    }
    part chost : ClosureHost;

    // Blocking: one host, one distinct leaf type per non-finite shape, so each
    // query reaches exactly one blocked member. `nonunique` is deliberately
    // excluded here -- a nonunique subsetting of a unique feature emits a
    // load-error diagnostic (b1-probe-evidence.md note 4) that would make this
    // whole fixture unloadable; its blocking is proven by the Phase-1 mock-node
    // truth table instead.
    part def LeafN;
    part def LeafStar;
    part def LeafRange;
    part def LeafOrdered;
    part def BlockHost {
        attribute n : Integer = 4;
        part n_member : LeafN [n];
        part star_member : LeafStar [*];
        part range_member : LeafRange [0..5];
        part ordered_member : LeafOrdered [3] ordered;
    }
    part bhost : BlockHost;
}
