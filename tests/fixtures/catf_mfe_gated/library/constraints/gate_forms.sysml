/*
 * Constraint-definition library for the CATF gated derivative.
 *
 * Two forms, both over bare `Real` formals with predicates written over formals only
 * (the blessed bindings-only gate shape, rulings-20260812 Q4). Neither carries a `[unit]`
 * literal: the toolchain does not check units on constraint bindings at all, so the unit
 * correctness of every binding here is human-owned (owner-disposition.md, unit-check column).
 */
package CATFGateForms {
    public import ScalarValues::*;

    constraint def PositiveQuantity {
        in quantity : Real;
        quantity > 0
    }

    constraint def FractionWithinBand {
        in part_power : Real;
        in whole_power : Real;
        in lower_frac : Real;
        in upper_frac : Real;
        part_power > whole_power * lower_frac and part_power < whole_power * upper_frac
    }
}
