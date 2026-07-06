package PlantValuesDesign {
    private import ScalarValues::*;
    private import PlantValuesLib::*;

    // The plant instance — a part USAGE typed by the BASE 'Power Plant' def, with
    // usage-level overrides/retypes supplying the three subsystem values. Exactly
    // the fusion-tea hif_plant shape (designs/hif_ife/hif_plant.sysml): a usage
    // typed by 'IFE Power Plant' with `part :>> driver : 'HIF Driver'` and bare
    // `part :>> target_factory { ... }` / `part :>> chamber { ... }` blocks.
    //
    // The cross-part consumer calc `cost_calc` is INHERITED from 'Power Plant' and
    // instantiates for this usage; its three inputs read `driver.efficiency`,
    // `target_factory.cost_per_target`, and `chamber.cost_per_unit`. The current
    // pipeline cannot wire these usage-level values to the calc inputs, so each
    // falls to a valueless Step-4 entry point that the calc still wires — V11 trips.
    part plant : 'Power Plant' {

        // Mechanism (a): usage-level retype to the subtype def, whose `:>> efficiency`
        // literal supplies the value cross-part.
        part :>> driver : 'Hif Driver';

        // Mechanism (b): bare no-retype override block — the shape no current fixture
        // contains. The literal feeds the plant calc's `target_cost` input cross-part.
        part :>> target_factory {
            :>> cost_per_target = 10.0;
        }

        // Mechanism (c): two-hop cross-part chain. The value is supplied through a
        // nested override block reaching `chamber.liner.cost_per_unit`. The plant calc
        // reads it cross-part; the current pipeline cannot wire the nested value to the
        // inherited calc input.
        part :>> chamber {
            part :>> liner {
                :>> cost_per_unit = 7.0;
            }
        }
    }
}
