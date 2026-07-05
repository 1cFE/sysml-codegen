package RetypeDesign {
    private import RetypeLibrary::*;

    part retype_design {
        // Retyped usage: the_variant.driver is redefined to the subtype 'HIF Driver'.
        // Superset indexing keys it under BOTH 'IFE Driver' and 'HIF Driver', so it
        // instantiates hif_calc (subtype), ife_calc (supertype, preserved), and the
        // single shared_calc winner (HIF, via the collision tiebreak).
        part the_variant : Variant;

        // Shape 5 (out-of-scope negative): a PLAIN subtype-typed usage. Its .types
        // excludes the user supertype (B2-plain), so it is keyed under 'HIF Driver'
        // only — the 'IFE Driver'-owned template MUST NOT reach it.
        part plain_hif : 'HIF Driver';
    }
}
