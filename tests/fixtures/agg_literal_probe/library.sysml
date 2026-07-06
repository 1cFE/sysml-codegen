package AggLiteralProbeLibrary {
    private import ScalarValues::Real;
    private import NumericalFunctions::sum;

    // Leaf part carrying the attribute the aggregation sums over.
    part def 'Module' {
        attribute cost : Real;
    }

    // Abstract base holds the redefinable aggregation target.
    abstract part def 'Costed Assembly' {
        attribute total_cost : Real;
    }

    // Aggregation whose RHS mixes a sum(...) term with a NUMERIC LITERAL (5.0).
    // Row-D / REQ-AST-10 probe: the literal operand must dispatch to the literal
    // branch of `_walk_aggregation_ast`, not the invocation catch-all. Before the
    // Item-8 hoist, every SysIDE node's derived `.function.name` made 5.0 hit the
    // invocation catch-all first -> has_unsupported_nodes=True and the literal was
    // swallowed. No other committed fixture has a literal-bearing aggregation, so
    // this is the sole fixture the byte-identity gate permits to change.
    part def 'Assembly' :> 'Costed Assembly' {
        part module : 'Module' [3];
        :>> total_cost = sum(module.cost) + 5.0;
    }
}
