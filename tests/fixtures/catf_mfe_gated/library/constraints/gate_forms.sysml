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

    /*
     * A9's ruled form: a two-sided band at 1% relative around `count * each_capacity`
     * (owner-disposition.md Group A, A9 — [OWNER 2026-08-13]).
     *
     * Unlike its two siblings above, this form is dimension-specific. A constraint formal's
     * port takes its unit from the formal's own declaration, so bare `Real` formals project
     * `unit_text=None` and collide with the calc lane's authored units on the same design
     * attributes. The unit comments below are therefore load-bearing, and a product band over
     * another dimension needs its own definition.
     */
    constraint def ProductWithinBand {
        in observed : Real;        // m³/s
        in count : Real;           // Dimensionless
        in each_capacity : Real;   // m³/s
        in rel_tol : Real;         // Dimensionless
        observed > count * each_capacity * (1.0 - rel_tol) and
        observed < count * each_capacity * (1.0 + rel_tol)
    }
}
