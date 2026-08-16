/*
 * A one-segment reference whose exact leaf is a `PartUsage`-owned *calculation usage*.
 *
 * `comp_a::twice` names the calculation itself, not one of its outputs. SysIDE accepts
 * the expression -- a calculation usage conforms to its returned value -- and resolves
 * it to the exact `twice` declaration owned by `comp_a`. The owner is a live `PartUsage`,
 * so exact-owner anchoring selects `comp_a`'s occurrence, and that occurrence carries no
 * attribute or computed target for a calculation-usage leaf.
 *
 * This is the authored shape that reaches the missing-leaf-target refusal in
 * `_resolve_direct_reference`. The elaborator refuses by name instead of picking one of
 * `twice`'s outputs on the author's behalf.
 */
package CalcUsageLeafOwner {
    private import ScalarValues::*;

    calc def 'Twice' {
        in v : Real;
        return result : Real = v * 2.0;
    }

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' {
            :>> length = 3.0;
            calc twice : 'Twice' { in v = length; }
        }

        part comp_b : 'Component' {
            :>> length = 7.0;
            attribute doubled : Real = comp_a::twice * 2.0;
        }
    }

    part plant : 'Plant';
}
