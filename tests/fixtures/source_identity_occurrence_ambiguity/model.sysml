package source_identity_occurrence_ambiguity {
    private import ScalarValues::*;

    // SOURCE-IDENTITY Item 4 focused ambiguity fixture (see PROVENANCE.md).
    // C9/C10: a definition-level referent consumed from a context that
    // contains TWO concrete occurrences of the definition. C9 is owner-qualified
    // and refuses a lineage miss without inspecting descendants. C10 is bare and
    // retains the named ambiguity outcome. Neither can first-pick.

    calc def 'Reading Consumer' {
        in attribute value_in : Real;
        out attribute value_out : Real = value_in * 2.0;
    }

    part def 'Amb Sensor' {
        attribute reading : Real default 1.0;
    }

    part def 'Amb Bay' {
        private import 'Amb Sensor'::*;

        part sensor_a : 'Amb Sensor';
        part sensor_b : 'Amb Sensor';

        // C9: owner-qualified (definition qualifier) form.
        calc amb_qual_calc : 'Reading Consumer' {
            in value_in = 'Amb Sensor'::reading;
        }
        // C10: bare renamed, def context (via the import), same def-level referent.
        calc amb_bare_calc : 'Reading Consumer' {
            in value_in = reading;
        }
    }

    part amb_bay : 'Amb Bay';
}
