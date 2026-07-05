package ReturnStylesLibrary {
    private import ScalarValues::Real;

    // Style A (control): fully-handled `in attribute` / `out attribute` form.
    // All members are AttributeUsage; unchanged by the SC-2 filter relaxation.
    calc def ControlA {
        in attribute a : Real;
        out attribute y : Real = a * 2;
    }

    // Style B: named inline `return` (ReferenceUsage Out). The return expression
    // lives on the ReferenceUsage, so `y` auto-implements (REQ-EXT-10, I5).
    calc def NamedReturnB {
        in attribute b : Real;
        return y : Real = b * 3;
    }

    // Bare `in` (ReferenceUsage In). The input `x` must land in input_attributes
    // even though it is not an `in attribute` (REQ-EXT-10).
    calc def BareInC {
        in x : Real;
        out attribute y : Real = x * 4;
    }

    // Style D: `return attribute` result plus a body assignment. The result `y`
    // is an AttributeUsage(Out); the body assignment is a direction-None
    // ReferenceUsage sharing the name `y`. `y` must appear once with no
    // auto-impl (degraded — expression capture deferred) and no phantom member
    // (REQ-EXT-12, I2).
    calc def StyleD {
        in attribute d : Real;
        return attribute y : Real;
        y = d * 5;
    }
}
