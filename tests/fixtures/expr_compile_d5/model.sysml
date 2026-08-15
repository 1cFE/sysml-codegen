package ExprCompileD5 {
    doc /*
    Auto-implementation classification and its stub fallback, in one model.

    This is the exact-route replacement specimen for the expression-compilation
    end-to-end proof that ``solar_battery_model``, ``catf_mfe_model`` and
    ``chain_spike_model`` carried. All three are ratified ``expected-collapse``
    rows the exact route refuses, and no fixture the exact route accepts emits a
    stub, so the *classification* claim (some calc defs compile, some do not)
    had no specimen left at all.

    The model holds four calc defs on purpose:

      * ``ProductCalc`` and ``RatioCalc`` — plain arithmetic, must auto-implement;
      * ``PowerCalc`` — exponent and precedence, must auto-implement;
      * ``OpaqueCalc`` — an ``out`` attribute with **no** expression, so there is
        nothing to compile. It must fall back to a ``NotImplementedError`` stub
        and must be the only row in the implementation backlog.

    Every binding is in the D-5 form (``in <formal>_in = <attribute>``).

    **Source**: authored for recovery plan Gate 4C, row L-201
    **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
    **Last Updated**: 2026-08-11
    */

    private import ScalarValues::Real;

    calc def ProductCalc {
        doc /*
        A product and a sum over it. Compilable.

        **Source**: authored for Gate 4C; the arithmetic is the fixture's own
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        in attribute width_in : Real;
        in attribute height_in : Real;
        in attribute margin_in : Real default := 4.0;

        out attribute area : Real = width_in * height_in;
        out attribute padded_area : Real = area + margin_in;
    }

    calc def RatioCalc {
        doc /*
        A division with a parenthesised denominator. Compilable.

        **Source**: authored for Gate 4C; the arithmetic is the fixture's own
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        in attribute numerator_in : Real;
        in attribute offset_in : Real;
        in attribute divisor_in : Real;

        out attribute ratio : Real = (numerator_in + offset_in) / divisor_in;
    }

    calc def PowerCalc {
        doc /*
        An exponent mixed with a product, to pin operator precedence. Compilable.

        **Source**: authored for Gate 4C; the arithmetic is the fixture's own
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        in attribute base_in : Real;
        in attribute exponent_in : Real;
        in attribute scale_in : Real default := 0.5;

        out attribute scaled_power : Real = scale_in * base_in ** exponent_in;
    }

    calc def OpaqueCalc {
        doc /*
        An output with no expression: nothing to compile, so the generator must
        emit a stub rather than invent a body.

        **Source**: authored for Gate 4C as the stub-fallback trigger
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        in attribute measurement_in : Real;

        out attribute correlated_value : Real;
    }

    part rig {
        doc /*
        The concrete rig: one usage of each calc def.

        **Source**: authored for Gate 4C
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        attribute width : Real = 6.0;
        attribute height : Real = 2.5;
        attribute offset : Real = 5.0;
        attribute divisor : Real = 4.0;
        attribute base : Real = 3.0;
        attribute exponent : Real = 2.0;
        attribute measurement : Real = 12.0;

        calc product : ProductCalc {
            in width_in = width;
            in height_in = height;
        }

        calc ratio : RatioCalc {
            in numerator_in = product.padded_area;
            in offset_in = offset;
            in divisor_in = divisor;
        }

        calc power : PowerCalc {
            in base_in = base;
            in exponent_in = exponent;
        }

        calc opaque : OpaqueCalc {
            in measurement_in = measurement;
        }
    }
}
