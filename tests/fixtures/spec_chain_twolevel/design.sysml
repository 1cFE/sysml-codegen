package TwoLevelDesign {
    private import TwoLevelLib::*;

    // The two-level shape, EXACTLY as fusion-tea authors it
    // (designs/hif_ife/hif_plant.sysml:23): a part USAGE typed by the BASE def
    // 'IFE Power Plant', with an inline `part :>> driver : 'HIF Driver'` retype on
    // the usage itself. lcoe_calc is INHERITED from 'IFE Power Plant' (declared on the
    // base) and instantiates for this usage; its binding `driver.cost_per_joule` must
    // reach 'HIF Driver's `:>> cost_per_joule = meier_cost.gamma`.
    //
    // The gap: usage_type_map indexes retypes keyed by (part-DEF QN, usage-name); this
    // retype lives on a part USAGE, so it is NOT indexed. The Phase-7 type-select keys
    // on lcoe_calc's declaring def ('IFE Power Plant') and finds only the base
    // 'IFE Driver' (no cost_per_joule redefinition) -> no rewrite -> the pin stays a
    // library-default entry point (unwired). This is the fusion-tea WI-015 mismatch.
    part hif_plant : 'IFE Power Plant' {
        part :>> driver : 'HIF Driver';
    }
}
