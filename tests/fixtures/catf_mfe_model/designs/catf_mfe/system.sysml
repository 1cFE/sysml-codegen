// CATF MFE Reference Design - System Integration
// Phase 3: Structure epic - Complete CATF MFE design instance

package CATF_MFE {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    // Import thermal load calc def
    private import FusionAnalysesThermalLoads::AuxiliarySystemsPower;

    // Import subsystem instances
    private import CATFMFEMagnets::catf_tf_system;
    private import CATFMFEHeating::catf_heating;
    private import CATFMFEVacuum::catf_vacuum_vessel;
    private import CATFMFEVacuum::catf_vacuum_pumping;
    private import CATFMFETritium::catf_tritium;
    private import CATFMFEBlanket::catf_blanket;
    private import CATFMFEPhysics::catf_physics;

    doc /*
    CATF Magnetic Fusion Energy (MFE) reference design - System integration.

    This package integrates all CATF MFE design components:
    - Magnets (TF, PF, CS) from magnets.sysml
    - Radial build (13 layers) from radial_build.sysml
    - Breeding blanket from blanket.sysml
    - Shield assembly from shield.sysml
    - Vacuum system from vacuum.sysml

    **Design Concept**: Spherical tokamak with HTS magnets
    **Source**: PyFECONS baseline configuration
    **Reference**: /home/reid/apps/PyFECONS/customers/CATF/mfe/DefineInputs.py
    **Phase**: Phase 3 - Structure Epic
    **Status**: Component instances complete, system integration in progress
    **Last Updated**: 2025-11-01
    */

    part catf_mfe_plant {
        doc /*
        CATF MFE fusion power plant - reference design instance.

        This instance demonstrates:
        - Usages pattern: snake_case naming
        - Attribute binding with specific values
        - Subsystem composition
        - Traceability to PyFECONS baseline

        **Design Parameters**:
        - Confinement: Magnetic (tokamak)
        - Magnet technology: High-temperature superconductor (HTS)
        - Target net power: ~300 MW electric
        - Design lifetime: 30 years
        - Target availability: 85%

        **Source**: PyFECONS CATF MFE baseline
        **Reference**: customers/CATF/mfe/DefineInputs.py
        **Last Updated**: 2025-10-31
        */

        attribute net_electric_power : Real = 300.0 {
            doc /*
            Target net electrical power output.

            **Value**: 300 MW (target)
            **Source**: CATF MFE baseline target
            **Note**: Actual value calculated in Physics epic from power balance
            */
        }

        attribute availability : Real = 0.85 {
            doc /*
            Plant availability factor (fraction of time producing power).

            **Value**: 0.85 (85%)
            **Source**: Industry standard for baseload plants (REFERENCE.md)
            **Note**: Refined in later phases with maintenance schedule modeling
            */
        }

        attribute lifetime_years : Real = 30.0 {
            doc /*
            Design lifetime of the plant.

            **Value**: 30 years
            **Source**: Typical fusion plant lifetime (REFERENCE.md)
            **Note**: Standard assumption for LCOE calculation
            */
        }

        attribute lcoe : Real {
            doc /*
            Levelized cost of electricity (USD/MWh).

            **Target**: <= 80 USD/MWh (preferred <= 60)
            **Source**: Economic Viability Requirement (requirements.sysml)
            **Status**: TO BE CALCULATED in Costing epic
            **Method**: LCOE = (Capital_Recovery × TDC + Annual_O&M) / Annual_Energy
            */
        }

        attribute q_engineering : Real {
            doc /*
            Engineering gain factor (net electric / auxiliary power).

            **Target**: >= 1.1 (net power), preferred >= 1.5
            **Source**: Net Power Requirement (requirements.sysml)
            **Status**: TO BE CALCULATED in Physics epic
            **Method**: Q_eng = P_electric_net / P_auxiliary
            */
        }

        attribute tbr : Real {
            doc /*
            Tritium breeding ratio.

            **Target**: >= 1.05 (with margin for losses and startup)
            **Source**: Tritium Self-Sufficiency Requirement (requirements.sysml)
            **Status**: TO BE CALCULATED in Physics epic
            **Method**: Neutronics calculation with blanket configuration
            */
        }

        part fusion_island {
            doc /*
            Core fusion reactor system (CAS22: Reactor Plant Equipment).

            **Composition**:
            - Magnet system: TF, PF, CS coils (see magnets.sysml)
            - Heating system: NBI + RF auxiliary heating (see heating.sysml)
            - Vacuum system: vessel + cryogenic pumping (see vacuum.sysml)
            - Tritium processing: fuel cycle management (see tritium.sysml)
            - Breeding blanket: Li2TiO3 solid breeder (see blanket.sysml)

            **Integration**: Each subsystem defined in separate file, composed here
            via cross-file references using ::> operator.

            **Status**: Level 7 architectural integrity restored (2025-11-17)
            **Reference**: Manifest expectations (manifest.yaml lines 8-14)
            **Last Updated**: 2025-11-17
            */

            // Subsystem composition (cross-file references)
            part magnets ::> catf_tf_system {
                doc /* TF+PF+CS magnet systems from magnets.sysml */
            }

            part heating ::> catf_heating {
                doc /* Neutral beam injection auxiliary heating from heating.sysml */
            }

            part vacuum ::> catf_vacuum_vessel {
                doc /* Primary vacuum boundary (vessel) from vacuum.sysml */
            }

            part tritium ::> catf_tritium {
                doc /* Fuel cycle processing from tritium.sysml */
            }

            part blanket ::> catf_blanket {
                doc /* Tritium breeding blanket from blanket.sysml */
            }

            part physics ::> catf_physics {
                doc /* Physics calculations from physics.sysml */
            }
        }

        part balance_of_plant {
            doc /*
            Power conversion and heat rejection systems.

            Includes:
            - Turbine plant equipment (CAS23)
            - Electric plant equipment (CAS24)
            - Miscellaneous plant equipment (CAS25)
            - Heat rejection system (CAS26)

            **Status**: Placeholder (detailed implementation in Structure epic)
            **Reference**: CAS accounts 23-26 (REFERENCE.md)
            */
        }

        part auxiliary_systems {
            doc /*
            Support systems for fuel handling and tritium processing.

            Includes:
            - Fuel handling and storage
            - Tritium processing and cleanup
            - Special materials (CAS27)

            **Status**: Placeholder (detailed implementation in Structure epic)
            **Reference**: CAS account 27 (REFERENCE.md)
            */
        }

        // Auxiliary systems power calculation
        calc auxiliary_load : AuxiliarySystemsPower {
            in gross_electric = 1546.72;  // MW - Temporary, will be cross-reference in Phase 5
            // auxiliary_fraction defaults to 0.009 (tuned to match ~14 MW)
        }

        attribute auxiliary_power : Real = auxiliary_load.auxiliary_power;  // EXPOSE for physics.sysml
    }
}
