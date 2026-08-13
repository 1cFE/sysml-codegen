package constraint_domain_inapplicable_plain_form {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def Positive {
        in v : Real;
        v > 0.0
    }

    // A bare `constraint` — a NON-asserted form — carrying a malformed marker. Severity by
    // cause normally grades the form, and a plain form never errors. A malformed
    // `@inapplicable:` is a different kind of cause: not a fact about the model, but a defect
    // in an instruction written to the tool. It halts by name whatever the form, because
    // silently ignoring it would be indistinguishable from never having written it.
    part def Host {
        attribute value : Real = 5.0;
        constraint plain_typo : Positive {
            doc /* @inapplicable no colon and no reason */
            in v = value;
        }
    }

    part the_host : Host;
}
