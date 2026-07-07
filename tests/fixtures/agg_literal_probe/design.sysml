package AggLiteralProbeDesign {
    private import ScalarValues::Real;
    private import AggLiteralProbeLibrary::*;

    part plant {
        part assembly : 'Assembly' {
            :>> module.cost = 10.0;
        }
    }
}
