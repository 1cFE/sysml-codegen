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
        // `Doubler(v = a)` is a calc-def invocation (InvocationExpression). The
        // point is any InvocationExpression as a binding RHS. (`max(a, b)` does
        // not resolve to a Behavior in this SysIDE build; a calc-def invocation
        // does.)
        calc c : PassthroughCalc {
            in x = Doubler(v = a);
        }
    }
}
