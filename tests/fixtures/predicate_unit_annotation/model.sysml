package predicate_unit_annotation {
    private import ScalarValues::*;
    private import SI::*;

    // =====================================================================
    // Defect A's third lane: a unit annotation inside an *inline asserted
    // predicate*.
    //
    //   `gap_width [m] >= 0.25 [m]`
    //
    // Only `source_form in ("inline", "requirement_constraint")` pushes a
    // usage's result_expression into the reference walk
    // (elaborate.py:1112-1117), so this shape — and not a definition-typed
    // predicate — is what reaches `_expression_references`. There the `[`
    // annotation's second operand is `SI::metre`, a standard-library element
    // with no feature slot, and the walk used to raise
    // SI_OCCURRENCE_MISSING.
    //
    // The annotations are *nested* under `>=` on purpose: an unwrap applied
    // at the predicate entry would be a no-op on this shape. The cure lands
    // at the head of the recursive walk.
    //
    // Both operands carry `[m]` because the profile admits an ordering only
    // over one category pair: `real/real` or `quantity/quantity`. A bare
    // `Real` feature reference is category `real` and an annotated literal is
    // category `quantity`, so `gap_width >= 0.25 [m]` blocks on
    // `block_ordering_category_pair` — a real profile limit, not the defect
    // under test. Giving the attribute a declared quantity type instead is
    // not available: codegen refuses `ISQBase::LengthValue` as an unsupported
    // exact type (SI_EDGE_DANGLING). Annotating both operands is what makes
    // this an *otherwise-supported* predicate, so the only thing standing
    // between the modeler and a working gate is Defect A.
    //
    // The predicate is an inequality, never `== <literal> [unit]`: the pinned
    // end state is a gate that *works* (admitted, catalogued, assessed), and
    // blessing a bare-quantity equality here would cut against Q4.
    //
    // Kept minimal on purpose — one part def, one attribute, one inline
    // asserted inequality, one Noop calc def so the pipeline has a module
    // (the `constraint_blocked_profile` idiom). `predicate_unit_annotation_bare`
    // is this model with `[m]` removed; both must resolve identically.
    //
    // **Source**: authored fixture (CONSTRAINT-SEMANTICS Item 4)
    // =====================================================================

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    part def GapHost {
        attribute gap_width : Real = 0.5 [m];
        assert constraint gap_guard {
            gap_width [m] >= 0.25 [m]
        }
    }

    part the_host : GapHost;
}
