package UnresolvableAttrProbeDesign {
    private import ScalarValues::Real;
    private import UnresolvableAttrProbeLibrary::*;

    // Design-side PartDef extending 'Base Component' with computed attrs
    // and a CalcUsage. Tests the same inherited-attr pattern as the
    // library-side 'Derived Component', but with additional patterns.
    //
    // Classification hypothesis:
    //   - If owned_members excludes inherited attrs AND QN is empty:
    //     Step 2d fallback -> not in sibling_attr_names -> UNRESOLVABLE
    //   - If QN resolves to 'Base Component':: namespace:
    //     Step 2c -> calc_refs -> EXPOSE_COMPUTED (misclassification)
    //   - If QN resolves to 'Design Derived':: namespace:
    //     Step 2b -> sibling_refs -> FORMULA (correct)
    part def 'Design Derived' :> 'Base Component' {
        attribute local_val : Real;

        // CalcUsage for mixed patterns
        calc my_calc : SimpleCalc {
            in x = local_val;
        }

        // Pattern D1: only inherited attrs
        // base_rate and base_factor inherited from 'Base Component'
        attribute inherited_product : Real = base_rate * base_factor;

        // Pattern D2: mix inherited + local
        attribute mixed_product : Real = base_rate * local_val;

        // Pattern D3: inherited attr + CalcUsage output
        // Combines FeatureChain (my_calc.result) with inherited attr (base_rate)
        attribute mixed_expose : Real = my_calc.result * base_rate;

        // Pattern D4: multi-term with inherited attrs
        attribute inherited_sum : Real = base_rate + base_factor + local_val;
    }

    // Instantiate the library-side 'Derived Component' with concrete values
    part derived_instance : 'Derived Component' {
        :>> base_rate = 10.0;
        :>> base_factor = 2.0;
        :>> local_multiplier = 3.0;
    }

    // Instantiate the design-side 'Design Derived' with concrete values
    part design_derived_instance : 'Design Derived' {
        :>> base_rate = 10.0;
        :>> base_factor = 2.0;
        :>> local_val = 5.0;
    }
}
