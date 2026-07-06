package SpecChainDesign {
    private import SpecChainLib::*;

    // Instantiate the retyped variant: its driver is the specialized 'HIF Driver',
    // so the lcoe consumer's `driver.cost_per_joule` must resolve to meier_cost.gamma.
    part spec_chain_plant : Variant;
}
