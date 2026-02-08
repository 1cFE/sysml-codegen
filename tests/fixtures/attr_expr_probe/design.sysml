package AttrExprProbeDesign {
    private import ScalarValues::Real;
    private import AttrExprProbeLibrary::*;

    part probe_design {

        // =============================================
        // ENTRY-POINT LITERALS (inputs to expressions)
        // =============================================
        attribute length : Real = 10.0;
        attribute width : Real = 5.0;
        attribute height : Real = 3.0;
        attribute rate : Real = 12.0;
        attribute markup : Real = 1.15;

        // Physics-inspired inputs (from CATF design values)
        attribute p_fusion : Real = 2600.0;
        attribute p_input : Real = 50.0;
        attribute eta_thermal : Real = 0.46;
        attribute eta_direct : Real = 0.85;
        attribute m_neutron : Real = 1.1;
        attribute f_pump : Real = 0.06;
        attribute eta_pump : Real = 0.5;
        attribute f_subsystem : Real = 0.03;

        // Geometry inputs (from CATF radial build)
        attribute r_inner : Real = 4.2;
        attribute r_outer : Real = 4.4;
        attribute r_major : Real = 3.0;
        attribute kappa : Real = 3.0;

        // =============================================
        // PATTERN A: Simple binary operations
        // (rewritten from chain_spike AreaCalc pattern)
        // =============================================

        // A1: multiplication (2 sibling refs) -- from AreaCalc
        attribute area : Real = length * width;

        // A2: division -- from ScientificQFactor
        attribute q_scientific : Real = p_fusion / p_input;

        // A3: addition
        attribute total_dim : Real = length + width;

        // A4: subtraction
        attribute net_length : Real = length - 1.0;

        // =============================================
        // PATTERN B: Multi-term and complex expressions
        // (rewritten from CATF CalcDefs)
        // =============================================

        // B1: three-term product
        attribute volume : Real = length * width * height;

        // B2: multi-term sum with coefficients -- perimeter formula
        attribute perimeter : Real = 2.0 * length + 2.0 * width;

        // B3: parenthesized sub-expression -- from TorusMinorRadius
        //   (r_inner + r_outer) / 2.0 - r_major
        attribute minor_radius : Real = (r_inner + r_outer) / 2.0 - r_major;

        // B4: two products summed -- from GrossElectricPower
        //   eta_thermal * p_thermal + eta_direct * p_alpha
        //   (but using entry-point attrs directly, not chained computed attrs)
        attribute gross_electric_simple : Real = eta_thermal * p_fusion + eta_direct * p_input;

        // B5: constant-fraction split -- from AlphaNeutronSplit (2 separate outputs)
        attribute p_alpha : Real = p_fusion * 3.52 / 17.58;
        attribute p_neutron : Real = p_fusion * 14.06 / 17.58;

        // B6: deep nesting with parentheses -- from BlanketThermalPower
        //   (m_n * p_n) + p_in + eta_th * (f_p * eta_p + f_sub) * (m_n * p_n)
        //   Uses entry-point attrs (not chained) to isolate nesting test
        attribute p_blanket_thermal : Real =
            (m_neutron * p_fusion) + p_input +
            eta_thermal * (f_pump * eta_pump + f_subsystem) * (m_neutron * p_fusion);

        // =============================================
        // PATTERN C: Chains (computed attr refs computed attr)
        // =============================================

        // C1: simple chain -- cost depends on computed 'area'
        attribute cost : Real = area * rate;

        // C2: multi-hop chain -- depends on computed 'cost'
        attribute marked_up_cost : Real = cost * markup;

        // C3: fan-in -- depends on TWO different computed attrs
        attribute cost_density : Real = cost / volume;

        // =============================================
        // PATTERN D: Mixed (computed attrs + CalcUsages)
        // =============================================

        // D1: computed attr feeds CalcUsage input
        calc scale_calc : ScaleCalc {
            in value = area;       // <-- 'area' is a computed attribute!
            in factor = markup;
        }

        // D2: CalcUsage output in an arithmetic expression (FeatureChain + Operator)
        attribute scaled_area : Real = scale_calc.result * 2.0;

        // D3: pure EXPOSE -- alias for CalcUsage output
        attribute scale_result : Real = scale_calc.result;

        // D4: multi-output CalcUsage with computed attr input + EXPOSE
        calc split : SplitCalc {
            in total = volume;     // <-- 'volume' is a computed attribute!
        }
        attribute half_vol : Real = split.half;
        attribute quarter_vol : Real = split.quarter;
    }
}
