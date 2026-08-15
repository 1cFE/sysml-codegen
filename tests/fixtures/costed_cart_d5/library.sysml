package CostedCartLibrary {
    doc /*
    Costed Component pattern in the D-5 binding form, sized for one test.

    This is the exact-route replacement specimen for the Costed Component
    pattern that ``solar_battery_model`` carried. That fixture is a ratified
    ``expected-collapse`` row (24x ``SI_SELF_BINDING``), so the exact route
    refuses it and its end-to-end proof could not follow the authority switch.
    The shape here is the same one, with the D-5 binding form and readable
    named aggregation terms.

    **Difference one — the D-5 binding form.** Every calc-usage binding renames
    the formal (``in area_in = area``) instead of binding a formal to an
    attribute of its own name.

    **Difference two — named aggregation terms.** Each child's contribution
    gets its own named attribute (``panel_capital``, ``caster_capital``) and
    the rollup adds those. This remains useful for readable rollups and
    independently inspectable per-role modules. It is no longer required to
    avoid ``SI_RENDERING_COLLISION``: a direct expression over same-named
    leaves keeps enough resolved child identity to distinguish its inputs.
    ``test_costed_component_exact_route.py::test_a_two_term_same_name_rollup_keeps_both_resolved_source_families``
    pins the direct form.

    What the shape carries, one trigger per bullet:
      * leaf parts with an embedded cost model, exposing their cost attributes
        by redefinition;
      * an allocation calc usage bound to usage literals, feeding an
        EXPOSE-pure attribute;
      * assemblies that aggregate over an arrayed child (``sum``) and over
        singleton children, three cost attributes each;
      * an ``idiot_index`` that divides two of those aggregations;
      * a FORMULA computed attribute (``throughput_units``) that a system-level
        calc usage consumes, so the consumer wires to a module output rather
        than to an entry point;
      * a system-level calc usage consuming the top assembly's rolled-up
        ``capital_cost``.

    Every factor is a binary-exact fraction (0.5, 0.25, 0.75) so the hand
    arithmetic in the specimens is exact, not approximate.

    **Source**: authored for recovery plan Gate 4C, rows L-199/L-203/L-198/L-201
    **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
    **Last Updated**: 2026-08-12
    */

    private import ScalarValues::Real;
    private import ScalarValues::Integer;
    private import NumericalFunctions::sum;

    // ============================================================
    // SECTION 1: THE COSTED INTERFACE
    // ============================================================

    abstract part def 'Costed Item' {
        doc /*
        Interface every cost-bearing part specializes.

        Leaf parts redefine the four attributes from their embedded cost model;
        assemblies redefine them as aggregations over their children.

        **Source**: the Costed Component pattern, as carried by solar_battery_model
        **Reference**: tests/fixtures/solar_battery_model/costing.sysml
        **Last Updated**: 2026-08-11
        */

        attribute capital_cost : Real;
        attribute raw_material_cost : Real;
        attribute fabrication_cost : Real;
        attribute idiot_index : Real;
    }

    // ============================================================
    // SECTION 2: LEAF COST CALC DEFS
    // ============================================================

    calc def DeckPanelCostCalc {
        doc /*
        Cost of one deck panel, driven by its area.

        **Source**: authored for Gate 4C; the arithmetic is the fixture's own
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        in attribute area_in : Real;

        in attribute cost_per_area_in : Real default := 12.0;
        in attribute fab_factor_in : Real default := 0.5;

        out attribute material_cost : Real = area_in * cost_per_area_in;
        out attribute fab_cost : Real = material_cost * fab_factor_in;
        out attribute total_cost : Real = material_cost + fab_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def CasterCostCalc {
        doc /*
        Cost of one caster, driven by its load rating.

        **Source**: authored for Gate 4C; the arithmetic is the fixture's own
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        in attribute load_rating_in : Real;

        in attribute cost_per_kg_in : Real default := 0.75;
        in attribute fab_factor_in : Real default := 0.5;

        out attribute material_cost : Real = load_rating_in * cost_per_kg_in;
        out attribute fab_cost : Real = material_cost * fab_factor_in;
        out attribute total_cost : Real = material_cost + fab_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def FrameRailCostCalc {
        doc /*
        Cost of the frame rail set, driven by total rail length.

        **Source**: authored for Gate 4C; the arithmetic is the fixture's own
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        in attribute length_in : Real;

        in attribute cost_per_m_in : Real default := 25.0;
        in attribute fab_factor_in : Real default := 0.5;

        out attribute material_cost : Real = length_in * cost_per_m_in;
        out attribute fab_cost : Real = material_cost * fab_factor_in;
        out attribute total_cost : Real = material_cost + fab_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def CrossBraceCostCalc {
        doc /*
        Cost of the cross-brace set, driven by brace count.

        **Source**: authored for Gate 4C; the arithmetic is the fixture's own
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        in attribute brace_count_in : Real;

        in attribute cost_per_brace_in : Real default := 5.0;
        in attribute fab_factor_in : Real default := 0.5;

        out attribute material_cost : Real = brace_count_in * cost_per_brace_in;
        out attribute fab_cost : Real = material_cost * fab_factor_in;
        out attribute total_cost : Real = material_cost + fab_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    // ============================================================
    // SECTION 3: ALLOCATION AND SYSTEM-LEVEL CALC DEFS
    // ============================================================

    calc def AllocationCostCalc {
        doc /*
        Minor-hardware allocation: fasteners per child plus wiring per kilogram.

        The allocation usage binds both drivers to usage literals, so this calc
        is the fixture's usage-literal entry-point source.

        **Source**: authored for Gate 4C; mirrors solar_battery's allocation model
        **Reference**: tests/fixtures/solar_battery_model/library.sysml
        **Last Updated**: 2026-08-11
        */

        in attribute child_count_in : Real;
        in attribute total_child_mass_in : Real;

        in attribute fastener_cost_per_child_in : Real default := 0.5;
        in attribute wiring_cost_per_kg_in : Real default := 2.0;
        in attribute material_share_in : Real default := 0.8;

        out attribute fastener_cost : Real = child_count_in * fastener_cost_per_child_in;
        out attribute wiring_cost : Real = total_child_mass_in * wiring_cost_per_kg_in;
        out attribute total_allocation : Real = fastener_cost + wiring_cost;
        out attribute material_portion : Real = total_allocation * material_share_in;
    }

    calc def AnnualizedFinancialCalc {
        doc /*
        Annualized capital charge: the rolled-up capital cost times a recovery factor.

        Its ``total_capex_in`` is what wires a system-level calc to the top
        assembly's aggregation output rather than to an entry point.

        **Source**: authored for Gate 4C; mirrors solar_battery's financial calc
        **Reference**: tests/fixtures/solar_battery_model/library.sysml
        **Last Updated**: 2026-08-11
        */

        in attribute total_capex_in : Real;
        in attribute recovery_factor_in : Real;

        out attribute annualized_capital_cost : Real = total_capex_in * recovery_factor_in;
    }

    calc def ThroughputCostCalc {
        doc /*
        Handling cost per year, driven by the computed throughput.

        Its ``throughput_units_in`` is what wires a system-level calc to a
        FORMULA computed attribute's module output.

        **Source**: authored for Gate 4C; the arithmetic is the fixture's own
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        in attribute throughput_units_in : Real;
        in attribute handling_cost_per_unit_in : Real;

        out attribute annual_handling_cost : Real =
            throughput_units_in * handling_cost_per_unit_in;
    }

    // ============================================================
    // SECTION 4: LEAF PART DEFINITIONS
    // ============================================================

    part def 'Deck Panel' :> 'Costed Item' {
        doc /*
        One deck panel. Arrayed inside the deck assembly.

        **Source**: authored for Gate 4C
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        attribute area : Real;

        calc cost_model : DeckPanelCostCalc {
            in area_in = area;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Caster' :> 'Costed Item' {
        doc /*
        One caster. Arrayed inside the deck assembly.

        **Source**: authored for Gate 4C
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        attribute load_rating : Real;

        calc cost_model : CasterCostCalc {
            in load_rating_in = load_rating;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Frame Rail Set' :> 'Costed Item' {
        doc /*
        The frame rails, one singleton child of the frame assembly.

        **Source**: authored for Gate 4C
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        attribute length : Real;

        calc cost_model : FrameRailCostCalc {
            in length_in = length;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Cross Brace Set' :> 'Costed Item' {
        doc /*
        The cross braces, the second singleton child of the frame assembly.

        **Source**: authored for Gate 4C
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        attribute brace_count : Real;

        calc cost_model : CrossBraceCostCalc {
            in brace_count_in = brace_count;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    // ============================================================
    // SECTION 5: ASSEMBLY DEFINITIONS
    // ============================================================

    part def 'Deck Assembly' :> 'Costed Item' {
        doc /*
        Deck sub-assembly: arrayed panels and casters, plus a minor-hardware
        allocation. Each child's contribution is its own named aggregation, and
        the rollup adds those names.

        **Source**: authored for Gate 4C
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        attribute panel_count : Integer default := 4;
        attribute caster_count : Integer default := 4;

        part deck_panel : 'Deck Panel' [panel_count];
        part caster : 'Caster' [caster_count];

        calc allocation_model : AllocationCostCalc {
            in child_count_in = 20.0;
            in total_child_mass_in = 50.0;
        }

        attribute misc_hardware_cost : Real = allocation_model.total_allocation;
        attribute misc_material_cost : Real = allocation_model.material_portion;

        attribute panel_capital : Real = sum(deck_panel.capital_cost);
        attribute caster_capital : Real = sum(caster.capital_cost);
        attribute panel_material : Real = sum(deck_panel.raw_material_cost);
        attribute caster_material : Real = sum(caster.raw_material_cost);
        attribute panel_fabrication : Real = sum(deck_panel.fabrication_cost);
        attribute caster_fabrication : Real = sum(caster.fabrication_cost);

        :>> capital_cost = panel_capital + caster_capital + misc_hardware_cost;
        :>> raw_material_cost = panel_material + caster_material + misc_material_cost;
        :>> fabrication_cost = panel_fabrication + caster_fabrication;
        :>> idiot_index = capital_cost / raw_material_cost;
    }

    part def 'Frame Assembly' :> 'Costed Item' {
        doc /*
        Frame sub-assembly: two singleton children, each exposed under its own
        name before the rollup adds them.

        **Source**: authored for Gate 4C
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        part frame_rail : 'Frame Rail Set';
        part cross_brace : 'Cross Brace Set';

        attribute rail_capital : Real = frame_rail.capital_cost;
        attribute brace_capital : Real = cross_brace.capital_cost;
        attribute rail_material : Real = frame_rail.raw_material_cost;
        attribute brace_material : Real = cross_brace.raw_material_cost;
        attribute rail_fabrication : Real = frame_rail.fabrication_cost;
        attribute brace_fabrication : Real = cross_brace.fabrication_cost;

        :>> capital_cost = rail_capital + brace_capital;
        :>> raw_material_cost = rail_material + brace_material;
        :>> fabrication_cost = rail_fabrication + brace_fabrication;
        :>> idiot_index = capital_cost / raw_material_cost;
    }

    part def 'Cart Plant' :> 'Costed Item' {
        doc /*
        Top assembly. Rolls the two sub-assemblies up one more level, which is
        what a system-level calc usage then consumes.

        **Source**: authored for Gate 4C
        **Reference**: .project/active/cutover-recovery/plan.md, Gate 4C
        **Last Updated**: 2026-08-11
        */

        part deck_assembly : 'Deck Assembly';
        part frame_assembly : 'Frame Assembly';

        attribute deck_capital : Real = deck_assembly.capital_cost;
        attribute frame_capital : Real = frame_assembly.capital_cost;
        attribute deck_material : Real = deck_assembly.raw_material_cost;
        attribute frame_material : Real = frame_assembly.raw_material_cost;
        attribute deck_fabrication : Real = deck_assembly.fabrication_cost;
        attribute frame_fabrication : Real = frame_assembly.fabrication_cost;

        :>> capital_cost = deck_capital + frame_capital;
        :>> raw_material_cost = deck_material + frame_material;
        :>> fabrication_cost = deck_fabrication + frame_fabrication;
        :>> idiot_index = capital_cost / raw_material_cost;
    }
}
