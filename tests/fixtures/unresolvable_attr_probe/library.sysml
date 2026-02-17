package UnresolvableAttrProbeLibrary {
    private import ScalarValues::Real;

    // Simple calc for mixed-pattern testing
    calc def SimpleCalc {
        in attribute x : Real;
        out attribute result : Real = x * 2.0;
    }

    // Base component: its attributes are inherited by subtypes.
    // The key question: when a subtype's expression references base_rate,
    // does SysIDE resolve the QN to BaseComponent:: or the subtype's namespace?
    part def 'Base Component' {
        attribute base_rate : Real;
        attribute base_factor : Real;
    }

    // PartDef-to-PartDef inheritance: 'Derived Component' specializes 'Base Component'.
    // Computed attrs here reference inherited attributes (base_rate, base_factor).
    //
    // Classification hypothesis:
    //   - If owned_members excludes inherited attrs AND QN is empty:
    //     Step 2d fallback -> not in sibling_attr_names -> UNRESOLVABLE
    //   - If QN resolves to 'Base Component':: namespace:
    //     Step 2c -> calc_refs -> EXPOSE_COMPUTED (misclassification)
    //   - If QN resolves to 'Derived Component':: namespace:
    //     Step 2b -> sibling_refs -> FORMULA (correct)
    part def 'Derived Component' :> 'Base Component' {
        attribute local_multiplier : Real;

        // L1: only inherited attrs in expression
        attribute inherited_product : Real = base_rate * base_factor;

        // L2: mix of inherited + locally-declared attrs
        attribute mixed_product : Real = base_rate * local_multiplier;
    }
}
