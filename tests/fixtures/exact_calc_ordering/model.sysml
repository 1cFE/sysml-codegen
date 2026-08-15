/**
 * Calculation payload ordering probe for the exact route.
 *
 * `SplitAndScale` carries the two shapes a rendered implementation has to get
 * right and a flat list of compiled results cannot express:
 *   - `scaled` is an undeclared intermediate: it must be assigned before it is
 *     used, and it is not one of the calculation's outputs.
 *   - `doubled_half` is a declared output that reads another declared output,
 *     so `half` must be assigned once and then returned by name.
 * Two declared outputs also pin that the returned values line up with the
 * projected output schema rather than with topological execution order.
 */
package ExactCalcOrdering {
    private import ScalarValues::*;

    calc def SplitAndScale {
        in attribute total : Real = 8.0;
        attribute scaled : Real = total * 2.0;
        out attribute half : Real = scaled / 4.0;
        out attribute doubled_half : Real = half * 2.0;
    }

    part def Rig {
        calc split : SplitAndScale;
    }

    part rig : Rig;
}
