/*
 * CATF MFE Magnet System Design Instances
 *
 * This file defines specific magnet instances for the Clean Air Task Force
 * MFE (Magnetic Fusion Energy) reference design, with parameters extracted
 * from PyFECONS baseline configuration.
 */

package CATFMFEMagnets {
    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    // Import thermal load calc def
    private import FusionAnalysesThermalLoads::MagnetCryogenicLoad;

    // Import radial build for geometry
    private import CATFMFERadialBuild::catf_radial_build;

    /*
     * TF Coil System Instance
     */
    part catf_tf_system {
        doc /*
        CATF MFE toroidal field coil system - spherical tokamak configuration with
        12 HTS CICC coils arranged toroidally around the plasma.

        **Source**: PyFECONS DefineInputs.py lines 97-109
        **Reference**: /home/reid/apps/PyFECONS/customers/CATF/mfe/DefineInputs.py
        **Design Type**: Spherical Tokamak
        **Technology**: High Temperature Superconductor, Cable-in-Conduit Conductor

        **Key Design Features**:
        - 12 discrete coils (vs continuous torus in conventional tokamaks)
        - Inner radius of 0.18 m (tight center column for ST)
        - High manufacturing factor (5.0) reflecting HTS CICC complexity
        - Operating at 20 K (LN2 subcooling or closed-cycle cryo)

        **Assumptions**:
        - Field values (field_on_axis, field_at_coil) to be calculated in physics epic
        - Structural material assumed SS316 (standard for magnet cases)
        - Current values to be determined from equilibrium calculations

        **Last Updated**: 2025-11-01
        */

        // From PyFECONS line 101
        attribute n_coils : Real = 12;

        // From PyFECONS line 102 - NOTE: r_centre is INNER radius for TF in ST geometry
        attribute r_centre : Real = 0.18 [m];

        // From PyFECONS line 103
        attribute z_centre : Real = 0.0 [m];

        // From PyFECONS line 104 (tf_dr defined at line 25)
        attribute thickness_radial : Real = 0.25 [m];

        // From PyFECONS line 105
        attribute thickness_vertical : Real = 0.35 [m];

        // From PyFECONS line 106
        attribute fraction_insulation : Real = 0.0;

        // From PyFECONS line 107
        attribute temperature_operating : Real = 20 [K];

        // From PyFECONS line 108
        attribute manufacturing_factor : Real = 5.0;

        // From PyFECONS line 100 - HTS_CICC
        attribute material_conductor : String = "HTS_CICC";

        // Assumed structural material (standard for magnet cases)
        attribute material_structure : String = "SS316";

        // TO BE CALCULATED in physics epic from equilibrium
        // Placeholder values based on typical ST parameters
        attribute field_on_axis : Real = 3.0 [T];
        attribute field_at_coil : Real = 12.0 [T];

        // TO BE CALCULATED from equilibrium and conductor specifications
        attribute current_total : Real = 50.0e6 [A];  // 50 MA placeholder

        // Cooling power calculation for TF system
        calc cryo_load : MagnetCryogenicLoad {
            in magnet_volume = catf_radial_build.magnet_volume_total;
            in magnet_surface_area = catf_radial_build.magnet_surface_area;
            in first_wall_area = catf_radial_build.first_wall_area;
            in p_neutron = 2079.41;  // MW - Temporary, will be cross-reference in Phase 5
            in b_field = field_at_coil;
            in operating_temp = temperature_operating;
            // carnot_efficiency defaults to 0.3
        }

        attribute cooling_power : Real = cryo_load.cooling_power;  // EXPOSE for physics.sysml
    }

    /*
     * PF Coil System Instances
     */

    part catf_pf1 {
        doc /*
        PF1 - Uppermost/lowermost PF coil pair, COPPER conductor.

        **Source**: PyFECONS DefineInputs.py lines 123-135
        **Position**: Far from plasma, z = ±3.73 m, r = 0.67 m
        **Material**: Copper (resistive conductor)
        **Function**: Plasma shaping and control at extremes

        **Note**: Only copper PF coil in the system. Copper used where
        field requirements are modest and resistive is more economical.

        **Last Updated**: 2025-11-01
        */

        // From PyFECONS line 124 - "PF1"
        attribute name : String = "PF1";

        // From PyFECONS line 127 - coil_count = 2 (symmetric pair)
        attribute coil_count : Real = 2;

        // From PyFECONS line 128
        attribute r_centre : Real = 0.67 [m];

        // From PyFECONS line 129
        attribute z_centre : Real = 3.73 [m];

        // From PyFECONS line 130
        attribute thickness_radial : Real = 0.3 [m];

        // From PyFECONS line 131
        attribute thickness_vertical : Real = 0.6 [m];

        // From PyFECONS line 132
        attribute fraction_insulation : Real = 0.0;

        // From PyFECONS line 133
        attribute temperature_operating : Real = 20 [K];

        // From PyFECONS line 134
        attribute manufacturing_factor : Real = 2.0;

        // From PyFECONS line 126 - COPPER
        attribute material_conductor : String = "Copper";

        // Structural material (assumed)
        attribute material_structure : String = "SS316";

        // TO BE CALCULATED from plasma control requirements
        attribute current : Real = 1.0e6 [A];  // Placeholder
    }

    part catf_pf2  {
        doc /*
        PF2 - Second PF coil pair, HTS CICC conductor.

        **Source**: PyFECONS DefineInputs.py lines 136-148
        **Position**: z = ±4.64 m, r = 0.9 m
        **Material**: HTS CICC (superconducting)

        **Last Updated**: 2025-11-01
        */

        attribute name : String = "PF2";
        attribute coil_count : Real = 2;
        attribute r_centre : Real = 0.9 [m];       // Line 141
        attribute z_centre : Real = 4.64 [m];      // Line 142
        attribute thickness_radial : Real = 0.3 [m];   // Line 143
        attribute thickness_vertical : Real = 0.6 [m]; // Line 144
        attribute fraction_insulation : Real = 0.0;    // Line 145
        attribute temperature_operating : Real = 20 [K]; // Line 146
        attribute manufacturing_factor : Real = 2.0;   // Line 147
        attribute material_conductor : String = "HTS_CICC"; // Line 139
        attribute material_structure : String = "SS316";
        attribute current : Real = 1.0e6 [A];  // Placeholder
    }

    part catf_pf3  {
        doc /*
        PF3 - Third PF coil pair, HTS CICC conductor.

        **Source**: PyFECONS DefineInputs.py lines 149-161
        **Position**: z = ±5.55 m, r = 1.28 m
        **Material**: HTS CICC (superconducting)
        **Note**: Larger radial thickness (0.5 m) than PF1/PF2

        **Last Updated**: 2025-11-01
        */

        attribute name : String = "PF3";
        attribute coil_count : Real = 2;
        attribute r_centre : Real = 1.28 [m];      // Line 154
        attribute z_centre : Real = 5.55 [m];      // Line 155
        attribute thickness_radial : Real = 0.5 [m];   // Line 156
        attribute thickness_vertical : Real = 0.6 [m]; // Line 157
        attribute fraction_insulation : Real = 0.0;    // Line 158
        attribute temperature_operating : Real = 20 [K]; // Line 159
        attribute manufacturing_factor : Real = 2.0;   // Line 160
        attribute material_conductor : String = "HTS_CICC"; // Line 152
        attribute material_structure : String = "SS316";
        attribute current : Real = 1.0e6 [A];  // Placeholder
    }

    part catf_pf4  {
        doc /*
        PF4 - Fourth PF coil pair, HTS CICC conductor.

        **Source**: PyFECONS DefineInputs.py lines 162-174
        **Position**: z = ±7.24 m, r = 2.72 m
        **Material**: HTS CICC (superconducting)
        **Note**: Larger radial thickness (0.75 m), smaller vertical (0.37 m)

        **Last Updated**: 2025-11-01
        */

        attribute name : String = "PF4";
        attribute coil_count : Real = 2;
        attribute r_centre : Real = 2.72 [m];      // Line 167
        attribute z_centre : Real = 7.24 [m];      // Line 168
        attribute thickness_radial : Real = 0.75 [m];  // Line 169
        attribute thickness_vertical : Real = 0.37 [m]; // Line 170
        attribute fraction_insulation : Real = 0.0;    // Line 171
        attribute temperature_operating : Real = 20 [K]; // Line 172
        attribute manufacturing_factor : Real = 2.0;   // Line 173
        attribute material_conductor : String = "HTS_CICC"; // Line 165
        attribute material_structure : String = "SS316";
        attribute current : Real = 1.0e6 [A];  // Placeholder
    }

    part catf_pf5  {
        doc /*
        PF5 - Fifth PF coil pair, HTS CICC conductor.

        **Source**: PyFECONS DefineInputs.py lines 175-187
        **Position**: z = ±7.24 m (same as PF4), r = 5.3 m (much larger radius)
        **Material**: HTS CICC (superconducting)
        **Note**: Very large radial thickness (1.8 m) for high field/current

        **Last Updated**: 2025-11-01
        */

        attribute name : String = "PF5";
        attribute coil_count : Real = 2;
        attribute r_centre : Real = 5.3 [m];       // Line 180
        attribute z_centre : Real = 7.24 [m];      // Line 181
        attribute thickness_radial : Real = 1.8 [m];   // Line 182
        attribute thickness_vertical : Real = 0.37 [m]; // Line 183
        attribute fraction_insulation : Real = 0.0;    // Line 184
        attribute temperature_operating : Real = 20 [K]; // Line 185
        attribute manufacturing_factor : Real = 2.0;   // Line 186
        attribute material_conductor : String = "HTS_CICC"; // Line 178
        attribute material_structure : String = "SS316";
        attribute current : Real = 1.0e6 [A];  // Placeholder
    }

    part catf_pf6  {
        doc /*
        PF6 - Sixth PF coil pair, HTS PANCAKE conductor.

        **Source**: PyFECONS DefineInputs.py lines 188-200
        **Position**: z = ±5.0 m, r = 9.34 m (large radius, outer position)
        **Material**: HTS PANCAKE (different winding topology than CICC)
        **Note**: Only pancake-wound PF coil. 1m x 1m cross-section.

        **Last Updated**: 2025-11-01
        */

        attribute name : String = "PF6";
        attribute coil_count : Real = 2;
        attribute r_centre : Real = 9.34 [m];      // Line 193
        attribute z_centre : Real = 5.0 [m];       // Line 194
        attribute thickness_radial : Real = 1.0 [m];   // Line 195
        attribute thickness_vertical : Real = 1.0 [m]; // Line 196
        attribute fraction_insulation : Real = 0.0;    // Line 197
        attribute temperature_operating : Real = 20 [K]; // Line 198
        attribute manufacturing_factor : Real = 2.0;   // Line 199
        attribute material_conductor : String = "HTS_REBCO"; // Pancake typically uses tape
        attribute material_structure : String = "SS316";
        attribute current : Real = 1.0e6 [A];  // Placeholder
    }

    part catf_pf7  {
        doc /*
        PF7 - Seventh PF coil pair, HTS CICC conductor with auto-CICC sizing.

        **Source**: PyFECONS DefineInputs.py lines 201-216
        **Position**: z = ±3.6 m, r = 9.34 m (large radius, mid-height)
        **Material**: HTS CICC (superconducting)

        **Note**: PyFECONS sets auto_cicc=True (line 213) with additional parameters
        at lines 214-215. This means conductor cross-section may be calculated
        automatically by PyFECONS based on field requirements. The thickness values
        here (1m x 1m) may represent allocated space rather than final conductor size.

        **Last Updated**: 2025-11-01
        */

        attribute name : String = "PF7";
        attribute coil_count : Real = 2;
        attribute r_centre : Real = 9.34 [m];      // Line 206
        attribute z_centre : Real = 3.6 [m];       // Line 207
        attribute thickness_radial : Real = 1.0 [m];   // Line 208
        attribute thickness_vertical : Real = 1.0 [m]; // Line 209
        attribute fraction_insulation : Real = 0.0;    // Line 210
        attribute temperature_operating : Real = 20 [K]; // Line 211
        attribute manufacturing_factor : Real = 2.0;   // Line 212
        attribute material_conductor : String = "HTS_CICC"; // Line 204
        attribute material_structure : String = "SS316";
        attribute current : Real = 1.0e6 [A];  // TO BE CALCULATED with auto_cicc
    }

    part catf_pf8  {
        doc /*
        PF8 - Eighth PF coil pair, HTS CICC conductor with auto-CICC sizing.

        **Source**: PyFECONS DefineInputs.py lines 217-232
        **Position**: z = ±2.2 m, r = 9.34 m (large radius, lower height than PF7)
        **Material**: HTS CICC (superconducting)

        **Note**: Also uses auto_cicc=True (line 228) like PF7. Final conductor
        sizing to be determined by equilibrium calculations in physics epic.

        **Last Updated**: 2025-11-01
        */

        attribute name : String = "PF8";
        attribute coil_count : Real = 2;
        attribute r_centre : Real = 9.34 [m];      // Line 221
        attribute z_centre : Real = 2.2 [m];       // Line 222
        attribute thickness_radial : Real = 1.0 [m];   // Line 223
        attribute thickness_vertical : Real = 1.0 [m]; // Line 224
        attribute fraction_insulation : Real = 0.0;    // Line 225
        attribute temperature_operating : Real = 20 [K]; // Line 226
        attribute manufacturing_factor : Real = 2.0;   // Line 227
        attribute material_conductor : String = "HTS_CICC"; // Line 219
        attribute material_structure : String = "SS316";
        attribute current : Real = 1.0e6 [A];  // TO BE CALCULATED with auto_cicc
    }

    /*
     * Central Solenoid Instance
     */

    part catf_cs_coil  {
        doc /*
        Central Solenoid for CATF MFE - provides flux swing for inductive startup
        and pulse flattop.

        **Source**: PyFECONS DefineInputs.py lines 110-122
        **Reference**: /home/reid/apps/PyFECONS/customers/CATF/mfe/DefineInputs.py
        **Technology**: HTS CICC for high field operation at 20 K

        **Key Design Features**:
        - Cylindrical geometry at machine center (r = 0.18 m inner)
        - Tall aspect (6.3 m height) for large flux swing
        - High manufacturing factor (10.0) reflecting precision and complexity

        **Physics Parameters**:
        - Flux swing and maximum field to be calculated in physics epic
        - Current capabilities to be determined from conductor specifications

        **Last Updated**: 2025-11-01
        */

        // From PyFECONS line 115 - inner radius
        attribute inner_radius : Real = 0.18 [m];

        // From PyFECONS line 117 - radial thickness (dr)
        attribute outer_radius : Real = 0.38 [m];  // inner_radius + thickness = 0.18 + 0.2

        // From PyFECONS line 118 - dz (height)
        attribute height : Real = 6.3 [m];

        // From PyFECONS line 116 - z_centre
        attribute z_centre : Real = 0.0 [m];

        // From PyFECONS line 114 - n_coils = 1 (single stack)
        // (No direct attribute for this in the part def, but noted)

        // From PyFECONS line 119
        attribute fraction_insulation : Real = 0.0;

        // From PyFECONS line 120
        attribute temperature_operating : Real = 20 [K];

        // From PyFECONS line 121
        attribute manufacturing_factor : Real = 10.0;

        // From PyFECONS line 113 - HTS_CICC
        attribute material_conductor : String = "HTS_CICC";

        // Structural material (assumed)
        attribute material_structure : String = "SS316";

        // TO BE CALCULATED in physics epic
        // Typical ST values as placeholders
        attribute flux_swing : Real = 15.0 [Wb];
        attribute field_max : Real = 14.0 [T];
        attribute current_max : Real = 20.0e6 [A];
    }
}
