package ElabMatrixAggregations {
    private import ScalarValues::*;

    calc def CostModel {
        in attribute base : Real;
        out attribute cost : Real = base * 10.0;
    }

    part def Costed {
        attribute capital_cost : Real;
    }

    part def Child :> Costed {
        attribute base_cost : Real = 2.0;
        attribute raw_material_cost : Real = 3.0;
        attribute fabrication_cost : Real = 4.0;
        attribute installation_cost : Real = 5.0;
        calc cost_model : CostModel { in base = base_cost; }
        :>> capital_cost = cost_model.cost;
    }

    part def Rollup {
        attribute producer_total : Real;
        attribute raw_total : Real;
        attribute fabrication_total : Real;
        attribute installation_total : Real;
    }

    part def Host :> Rollup {
        part permitting : Child;
        :>> producer_total = permitting.capital_cost + 1.0;
        :>> raw_total = permitting.raw_material_cost + 1.0;
        :>> fabrication_total = permitting.fabrication_cost + 1.0;
        :>> installation_total = permitting.installation_cost + 1.0;
    }

    part host : Host;
}
