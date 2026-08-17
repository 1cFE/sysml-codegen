package source_identity_mixed_consumers {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;

    // SOURCE-IDENTITY Item 4 foundation fixture (see PROVENANCE.md).
    // One exact supported route per assigned Appendix C cell: C8, C11, C12,
    // C13, C15, C24, C25 — plus a Path-A stamp route (C1-kin) for the
    // reference-derived-literal discriminator, a deep-path override (C19-kin
    // value-site evidence), a sum() aggregation term, and one authored usage
    // literal. Every form is inside the supported executable subset.

    calc def 'Reading Consumer' {
        in attribute value_in : Real;
        out attribute value_out : Real = value_in * 2.0;
    }

    // C24 declaration key: 'Source Identity Producer'::result.
    calc def 'Source Identity Producer' {
        in attribute base : Real;
        out attribute result : Real = base * 3.0;
    }

    constraint def 'Below Limit' {
        in attribute v : Real;
        v <= 1000.0
    }

    // ---- C8: one definition, two concrete occurrences, distinct overrides,
    //      one chain calculation per occurrence -------------------------------
    part def 'Twin Sensor' {
        attribute reading : Real default 1.0;
    }

    part def 'Twin Bay' {
        part sensor_a : 'Twin Sensor' {
            :>> reading = 11.0;
        }
        part sensor_b : 'Twin Sensor' {
            :>> reading = 22.0;
        }
        calc calc_a : 'Reading Consumer' {
            in value_in = sensor_a.reading;
        }
        calc calc_b : 'Reading Consumer' {
            in value_in = sensor_b.reading;
        }
    }

    // ---- C11: feature chain x mixed consumers (calc + constraint + agg) ----
    part def 'Rig' {
        attribute gain_setting : Real default 5.0;
    }

    part def 'Station Rollup' {
        attribute station_total : Real;
    }

    part def 'Station' :> 'Station Rollup' {
        part rig : 'Rig' {
            :>> gain_setting = 42.0;
        }
        calc chain_calc : 'Reading Consumer' {
            in value_in = rig.gain_setting;
        }
        assert constraint chain_guard : 'Below Limit' {
            in v = rig.gain_setting;
        }
        :>> station_total = rig.gain_setting + 100.0;
    }

    // ---- C12: definition-owned qualification on-lineage x mixed consumers ---
    part def 'Qual Plant' {
        attribute level : Real default 7.0;
        calc qual_calc : 'Reading Consumer' {
            in value_in = 'Qual Plant'::level;
        }
        assert constraint qual_guard : 'Below Limit' {
            in v = 'Qual Plant'::level;
        }
    }

    part def 'Qual Rollup' {
        attribute qual_total : Real;
    }

    part def 'Qual Station' :> 'Qual Rollup' {
        part qual_plant : 'Qual Plant' {
            :>> level = 70.0;
        }
        :>> qual_total = qual_plant.level + 1.0;
    }

    // ---- C13: bare renamed (usage context) x mixed consumers ----------------
    part def 'Bare Rig' {
        attribute intensity : Real default 3.0;
    }

    part def 'Bare Rollup' {
        attribute bare_total : Real;
    }

    part def 'Bare Station' :> 'Bare Rollup' {
        part bare_rig : 'Bare Rig' {
            :>> intensity = 30.0;
            calc bare_calc : 'Reading Consumer' {
                in value_in = intensity;
            }
            assert constraint bare_guard : 'Below Limit' {
                in v = intensity;
            }
        }
        :>> bare_total = bare_rig.intensity + 2.0;
    }

    // ---- C15: cross-owner parent attribute; parent-owned aggregation +
    //      constraint + child-part calculation --------------------------------
    part def 'Child Unit' {
        attribute unit_size : Real = 1.0;
    }

    part def 'Parent Rollup' {
        attribute parent_total : Real;
    }

    part def 'Parent Unit' :> 'Parent Rollup' {
        attribute shared_rate : Real default 4.0;
        part child : 'Child Unit' {
            calc child_calc : 'Reading Consumer' {
                in value_in = shared_rate;
            }
        }
        assert constraint parent_guard : 'Below Limit' {
            in v = shared_rate;
        }
        :>> parent_total = shared_rate * 1.5;
    }

    // ---- C24: feature chain to a computed value (producer channel);
    //      occurrence key: source_identity_computed.producer_calc -------------
    part def 'Computed Unit' {
        attribute base_rate : Real = 2.0;
        calc producer_calc : 'Source Identity Producer' {
            in base = base_rate;
        }
    }

    part def 'Computed Rollup' {
        attribute computed_total : Real;
    }

    part def 'Computed Station' :> 'Computed Rollup' {
        part source_identity_computed : 'Computed Unit';
        calc computed_calc : 'Reading Consumer' {
            in value_in = source_identity_computed.producer_calc.result;
        }
        assert constraint computed_guard : 'Below Limit' {
            in v = source_identity_computed.producer_calc.result;
        }
        :>> computed_total = source_identity_computed.producer_calc.result + 1.0;
    }

    // ---- C25: bare renamed x mixed definition/usage binding contexts,
    //      single occurrence :>> override, 2 calculations ---------------------
    part def 'Avail Plant' {
        attribute availability : Real default 0.9;
        calc def_authored_calc : 'Reading Consumer' {
            in value_in = availability;
        }
    }

    part def 'Avail Design Ctx' {
        part avail_plant : 'Avail Plant' {
            :>> availability = 0.8;
            calc usage_authored_calc : 'Reading Consumer' {
                in value_in = availability;
            }
        }
    }

    // ---- Path-A stamp route (C1-kin): bare renamed def-context binding whose
    //      occurrence override the legacy VBR literal-stamps -------------------
    part def 'Stamp Plant' {
        attribute efficiency : Real default 0.5;
        calc stamp_calc : 'Reading Consumer' {
            in value_in = efficiency;
        }
        // Authored usage literal (value-site kind 3): its evidence must stay
        // distinguishable from the stamped reference-derived literal above.
        calc lit_calc : 'Reading Consumer' {
            in value_in = 9.5;
        }
    }

    // ---- sum() aggregation term over a fixed multiplicity --------------------
    part def 'Bank Cell' {
        attribute cell_cost : Real = 6.0;
    }

    part def 'Bank Rollup' {
        attribute bank_total : Real;
    }

    part def 'Bank' :> 'Bank Rollup' {
        part cell : 'Bank Cell'[3];
        :>> bank_total = sum(cell.cell_cost);
    }

    // ---- C19-kin deep-path occurrence override (value-site evidence) --------
    // Dedicated chain: 'Deep Panel'::deep_rig carries no value binding of its
    // own, so the deep-path override is the only value supplier.
    part def 'Deep Panel' {
        part deep_rig : 'Rig';
    }

    part def 'Deep Design' {
        part panel_two : 'Deep Panel' {
            :>> deep_rig.gain_setting = 43.0;
        }
    }

    // ---- concrete design instantiations --------------------------------------
    part twin_bay : 'Twin Bay';
    part station : 'Station';
    part qual_station : 'Qual Station';
    part bare_station : 'Bare Station';
    part parent_unit : 'Parent Unit' {
        :>> shared_rate = 40.0;
    }
    part computed_station : 'Computed Station';
    part avail_ctx : 'Avail Design Ctx';
    part bank : 'Bank';
    part deep_design : 'Deep Design';
    part stamp_plant : 'Stamp Plant' {
        :>> efficiency = 0.75;
    }
}
