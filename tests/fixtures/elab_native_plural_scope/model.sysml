package ElabNativePluralScope {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;

    calc def Observe {
        in attribute sample : Real;
        out attribute result : Real = sample;
    }

    part def BaseLeaf {
        attribute value : Real default 2.0;

        // The binding materializes an implied redefinition of Observe::sample.
        calc observation : Observe {
            in sample = BaseLeaf::value;
        }
    }

    part def SpecializedLeaf :> BaseLeaf {
        :>> value = 7.0;
    }

    part def BaseContainer {
        attribute count : Integer = 2;
        part leaf : BaseLeaf[count];
        attribute total : Real = sum(leaf.value);
    }

    part def SpecializedContainer :> BaseContainer {
        part :>> leaf : SpecializedLeaf[count];
    }

    part def Plant {
        part selected : BaseContainer;
        part shadow : BaseContainer;
    }

    part plant : Plant {
        part :>> selected : SpecializedContainer;
    }

    attribute fleet_total : Real = sum(plant.selected.leaf.value);

    part dashboard {
        attribute observed_total : Real = sum(plant.selected.leaf.value);
    }
}
