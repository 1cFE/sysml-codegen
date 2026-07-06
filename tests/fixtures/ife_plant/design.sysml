package IfePlantDesign {
    private import ScalarValues::*;
    private import IfePlantLib::*;
    private import IfePlantSubsystems::radial_build;

    // Shape 3 (retyped nested part): a plant specialization that retypes the
    // driver to the subtype. The retyped driver instantiates hif_cost_calc
    // (subtype-owned) AND base_power_calc (supertype-preserved) — the Item 4/5 win.
    part def 'Hif Plant' :> 'Ife Power Plant' {
        doc /*
        HIF plant specialization: retypes the base driver to the HIF subtype.
        **Source**: authored fixture (Item 8)
        **Reference**: spec.md Fixture 2, shape 3 (retyped nested part)
        **Last Updated**: 2026-07-05
        */
        part :>> driver : 'Hif Driver';
    }

    // Main instantiation exercising shapes 3 (retyped driver) + 7 (siblings).
    part hif_plant : 'Hif Plant';

    // Shape 5 (plain-usage :>> override, mechanism C — currently dropped at
    // extraction): a PLAIN plant usage that redefines a plant attribute via :>>.
    part baseline_plant : 'Ife Power Plant' {
        :>> capacity_factor = 0.95;
    }

    // Shape 4 (cross-part calc-chain binding, mechanism B — deliberately unwired).
    // Mirrors catf_mfe's cryo_load / catf_radial_build pair: the imported,
    // separate-package radial_build exposes a valueless calc output
    // (magnet_volume_total = tf_coil.volume, reached through the nested tf_coil
    // part); magnet_system's cryo_load binds its magnet_volume input cross-package
    // to that exposed output. The current pipeline cannot wire this to a producer
    // channel, so magnet_volume falls to a valueless Step-4 fallback entry point
    // that the calc still wires — the known-incomplete baseline (expected to trip
    // V11 on the strict path, exactly like catf's dangling cryo_load.magnet_volume).
    part magnet_system {
        calc cryo_load : CryoLoad {
            in magnet_volume = radial_build.magnet_volume_total;
        }
    }
}
