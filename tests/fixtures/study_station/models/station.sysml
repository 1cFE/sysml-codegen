package PumpStation {
    private import ScalarValues::*;

    // A neutral study fixture, written for study-layer-to-codegen: a stormwater
    // pump station sized against the flow it must remove. Baseline arithmetic:
    // required_flow = 0.30 - 0.005 * 12.0 = 0.24; annual_cost = 0.24 * 8.0 *
    // 0.10 * 1000.0 = 192.0; pump_fit holds because 0.25 >= 0.24.

    calc def RequiredFlow {
        in attribute inflow : Real;
        in attribute rise_rate : Real;
        in attribute area : Real;
        out attribute required_flow : Real = inflow - rise_rate * area;
    }

    calc def PumpingCost {
        in attribute flow_rate : Real;
        in attribute head : Real;
        in attribute price : Real;
        out attribute annual_cost : Real = flow_rate * head * price * 1000.0;
    }

    constraint def CapacityCoversDemand {
        in attribute capacity : Real;
        in attribute demand_flow : Real;
        capacity >= demand_flow
    }

    part station {
        attribute design_inflow : Real = 0.30;
        attribute basin_area : Real = 12.0;
        attribute allowed_rise_rate : Real = 0.005;
        attribute installed_capacity : Real = 0.25;
        attribute pump_head : Real = 8.0;
        attribute energy_price : Real = 0.10;

        calc demand : RequiredFlow {
            in inflow = design_inflow;
            in rise_rate = allowed_rise_rate;
            in area = basin_area;
        }

        calc pumping : PumpingCost {
            in flow_rate = demand.required_flow;
            in head = pump_head;
            in price = energy_price;
        }

        assert constraint pump_fit : CapacityCoversDemand {
            in capacity = installed_capacity;
            in demand_flow = demand.required_flow;
        }
    }
}
