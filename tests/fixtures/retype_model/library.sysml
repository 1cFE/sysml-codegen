package RetypeLibrary {
    private import ScalarValues::Real;

    // Differently-named template calc owned by the supertype (shapes 2, 4).
    calc def IfeCalc {
        in attribute p : Real;
        out attribute ife_out : Real = p * 2.0;
    }

    // Differently-named template calc owned by the subtype (shapes 1, 4).
    calc def HifCalc {
        in attribute q : Real;
        out attribute hif_out : Real = q * 3.0;
    }

    // Same-named template calc on both owners (shape 3 collision). The subtype
    // redefines the supertype's usage under the same instance name 'shared_calc',
    // so both resolve to the same virtual QN -> most-specific-owner tiebreak (V9).
    calc def SharedCalc {
        in attribute s : Real;
        out attribute shared_out : Real = s + 1.0;
    }

    // Supertype 'IFE Driver': owns a differently-named template (ife_calc) plus the
    // same-named template (shared_calc).
    part def 'IFE Driver' {
        attribute power : Real = 10.0;

        calc ife_calc : IfeCalc {
            in p = power;
        }

        calc shared_calc : SharedCalc {
            in s = power;
        }
    }

    // Subtype 'HIF Driver' :> 'IFE Driver': owns a differently-named template
    // (hif_calc) and redefines the same-named template (shared_calc).
    part def 'HIF Driver' :> 'IFE Driver' {
        attribute torque : Real = 20.0;

        calc hif_calc : HifCalc {
            in q = torque;
        }

        // Redefine the supertype's same-named template. The binding is inherited
        // (overriding a bound feature value is illegal); the redefinition is a
        // HIF-owned CalculationUsage that collides with IFE's on the virtual QN.
        calc :>> shared_calc : SharedCalc;
    }

    // Two unrelated user typings on one usage (V10 incomparable branch). Neither
    // 'IFE Driver' nor 'Other Driver' specializes the other.
    part def 'Other Driver' {
        attribute mass : Real = 5.0;
    }

    // Two unrelated owned typings on one usage -> usage_type_map's incomparable
    // branch fires the V10 warning (deterministic sorted-first pick).
    part def MultiHolder {
        part multi : 'IFE Driver', 'Other Driver';
    }

    part def Facility {
        part driver : 'IFE Driver';
    }

    // Retyping design: Variant redefines Facility.driver to the subtype 'HIF Driver'.
    part def Variant :> Facility {
        part :>> driver : 'HIF Driver';
    }
}
