package AliasAggProbeDesign {
    private import ScalarValues::Real;
    private import AliasAggProbeLibrary::*;

    part plant {
        part assembly : 'Widget Assembly' {
            :>> widget.base_cost = 50.0;
        }
    }
}
