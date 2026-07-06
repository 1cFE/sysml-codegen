package IfePlantSubsystems {
    private import ScalarValues::*;
    private import IfePlantLib::*;

    // Shape 4 source half (mechanism B). A separate-package radial-build usage that
    // exposes a valueless calc output (magnet_volume_total = tf_coil.volume, reached
    // THROUGH the nested tf_coil part). The magnet subsystem in the design binds to
    // this cross-package — the reference the current pipeline cannot wire to a
    // producer channel (mirrors catf_mfe's CATFMFERadialBuild::catf_radial_build).
    part radial_build {
        part tf_coil : 'Coil';
        attribute magnet_volume_total : Real = tf_coil.volume_calc.volume;
    }
}
