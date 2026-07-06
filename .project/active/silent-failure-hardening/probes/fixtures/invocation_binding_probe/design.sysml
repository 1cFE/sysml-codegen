package InvocationBindingDesign {
    private import ScalarValues::Real;
    private import InvocationBindingLibrary::*;

    part probe {
        attribute a : Real = 10.0;
        attribute b : Real = 20.0;

        // Binding RHS is a function INVOCATION (InvocationExpression), not
        // FCE / FRE / literal / OperatorExpression. It is not one of the four
        // types the dispatch in _extract_single_binding handles, so it falls
        // through to the UNBOUND catch-all (usage_extractor.py:748).
        //
        // If `max(...)` does not parse in this SysIDE build, swap for another
        // invocation form (e.g. `min(a, b)` or a user function call). The point
        // is any InvocationExpression as a binding RHS.
        calc c : PassthroughCalc {
            in x = max(a, b);
        }
    }
}
