/**
 * CATF MFE Physics Calculations Instance
 *
 * Physics calculations for the CATF MFE fusion reactor design using
 * library calc definitions and cross-file structural references.
 *
 * Created: 2025-11-03
 * Updated: 2025-11-09 - Refactored to use library + structural coupling
 * Sources: PyFECONS DefineInputs.py, PowerBalance.py
 */
package CATFMFEPhysics {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    // Import power balance library calc definitions
    private import CATFGateForms::PositiveQuantity;
    private import CATFGateForms::FractionWithinBand;
    private import FusionPhysics::AlphaNeutronSplit;
    private import FusionPhysics::BlanketThermalPower;
    private import FusionPhysics::GrossElectricPower;
    private import FusionPhysics::NetElectricPower;

    // Import performance metric calc definitions from library
    private import FusionPhysics::ScientificQFactor;
    private import FusionPhysics::EngineeringQFactor;
    private import FusionPhysics::PlantEfficiency;

    // Import structural component instances for cross-file parasitic load references
    private import CATFMFEMagnets::catf_tf_system;          // For cooling_power
    private import CATFMFEBlanket::catf_blanket;            // For pump_power
    private import CATFMFEHeating::catf_heating;            // For wall_plug_power
    private import CATFMFEVacuum::catf_vacuum_pumping;      // For pump_power, cryo_power
    private import CATFMFETritium::catf_tritium;            // For processing_power
    private import CATF_MFE::catf_mfe_plant;                // For auxiliary_power

    /**
     * CATF MFE Physics Instance
     */
    part catf_physics {
        doc /*
        CATF MFE baseline physics: 2600 MW fusion, 50 MW input, Q_sci = 52

        Uses library calc definitions with cross-file bindings to structural
        component instances for parasitic power loads. This enables bottom-up
        power balance validation where parasitic loads are calculated from
        first principles rather than using empirical placeholders.

        **Source**: PyFECONS DefineInputs.py lines 52-70, PowerBalance.py
        **Validation**: Match PyFECONS PowerTable within 1-5%
        **Last Updated**: 2025-11-09
        */

        // Input parameters (from PyFECONS inputs.json)
        attribute p_fusion : Real = 2600.0;  // MW - Fusion power
        attribute p_input : Real = 50.0;     // MW - Auxiliary heating power delivered to plasma
        attribute m_neutron : Real = 1.1;    // Dimensionless - Neutron energy multiplication
        attribute eta_thermal : Real = 0.46; // Dimensionless - Thermal conversion efficiency
        attribute eta_direct : Real = 0.85;  // Dimensionless - Direct energy conversion efficiency (PyFECONS eta_de)
        attribute f_pump : Real = 0.06;      // Dimensionless - Pumping power fraction
        attribute eta_pump : Real = 0.5;     // Dimensionless - Pumping efficiency
        attribute f_subsystem : Real = 0.03; // Dimensionless - Subsystem power fraction

        // Calculation instances with library calc defs
        calc alpha_neutron_split : AlphaNeutronSplit {
            in p_fusion = catf_physics::p_fusion;
        }

        calc blanket_thermal : BlanketThermalPower {
            in p_neutron = alpha_neutron_split.p_neutron;
            in p_input = catf_physics::p_input;
            in m_neutron = catf_physics::m_neutron;
            in eta_thermal = catf_physics::eta_thermal;
            in f_pump = catf_physics::f_pump;
            in eta_pump = catf_physics::eta_pump;
            in f_subsystem = catf_physics::f_subsystem;
        }

        calc gross_electric : GrossElectricPower {
            in p_thermal = blanket_thermal.p_thermal;
            in p_alpha = alpha_neutron_split.p_alpha;
            in eta_thermal = catf_physics::eta_thermal;
            in eta_direct = catf_physics::eta_direct;
        }

        calc net_electric : NetElectricPower {
            in p_electric_gross = gross_electric.p_electric_gross;

            // CROSS-FILE BINDINGS to structural component parasitic loads
            // These replace the placeholder values from Phase 1
            in p_coils = catf_tf_system.cooling_power;          // From magnets.sysml (~15 MW)
            in p_heating = catf_heating.wall_plug_power;        // From heating.sysml (100 MW)
            in p_pumps = catf_blanket.pump_power;               // From blanket.sysml (~66 MW)
            in p_cryo = catf_vacuum_pumping.cryo_power;         // From vacuum.sysml (~0.5 MW)
            in p_vacuum = catf_vacuum_pumping.pump_power;       // From vacuum.sysml (~5 MW)
            in p_tritium = catf_tritium.processing_power;       // From tritium.sysml (~10 MW)
            in p_auxiliary = catf_mfe_plant.auxiliary_power;    // From system.sysml (~14 MW)
        }

        calc q_scientific : ScientificQFactor {
            in p_fusion = catf_physics::p_fusion;
            in p_input = catf_physics::p_input;
        }

        calc q_engineering : EngineeringQFactor {
            in p_electric_gross = gross_electric.p_electric_gross;
            in p_auxiliary_total = net_electric.p_parasitic_total;
        }

        calc plant_efficiency : PlantEfficiency {
            in p_fusion = catf_physics::p_fusion;
            in p_net = net_electric.p_net;
        }

        // Output attributes (exposed for validation and reporting)
        attribute p_alpha_out : Real = alpha_neutron_split.p_alpha;           // MW - Alpha power (520 MW)
        attribute p_neutron_out : Real = alpha_neutron_split.p_neutron;       // MW - Neutron power (2079 MW)
        attribute p_thermal_out : Real = blanket_thermal.p_thermal;           // MW - Blanket thermal power
        attribute p_electric_gross_out : Real = gross_electric.p_electric_gross;  // MW - Gross electric
        attribute p_electric_net_out : Real = net_electric.p_net;             // MW - Net electric to grid
        attribute q_sci_out : Real = q_scientific.q_sci;                      // Dimensionless - Scientific Q
        attribute q_eng_out : Real = q_engineering.q_eng;                     // Dimensionless - Engineering Q
        attribute f_recirc_out : Real = q_engineering.f_recirculating;        // Dimensionless - Recirculating fraction
        attribute eta_plant_out : Real = plant_efficiency.eta_plant;          // Dimensionless - Plant efficiency

        assert constraint net_power_viable : PositiveQuantity {
            doc /*
            Net power must be positive for viable power plant.
            This ensures Q_eng > 1.0
            */
            in quantity = p_electric_net_out;
        }

        assert constraint parasitic_fraction_ok : FractionWithinBand {
            doc /*
            Total parasitic loads should be reasonable (10-90% of gross).
            Upper bound ensures Q_eng > 1.1 (CATF minimum)
            */
            in part_power = net_electric.p_parasitic_total;
            in whole_power = gross_electric.p_electric_gross;
            in lower_frac = 0.10;
            in upper_frac = 0.90;
        }
    }
}
