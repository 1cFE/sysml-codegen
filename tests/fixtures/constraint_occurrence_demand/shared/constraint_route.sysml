package DemandShared {
    private import DemandSharedLibrary::*;

    part plant : Plant {
        :>> source.value = 17.0;
    }
}
