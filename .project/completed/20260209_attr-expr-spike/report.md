# Spike Report: Attribute Expression AST Discovery & Architecture Evaluation

**Generated:** 2026-02-08T20:00:41.702861
**Branch:** cost-pattern
**Epic:** ATTR-EXPR Item 1

```
======================================================================
Q1: AST Availability -- Do PartDef attributes have feature_value_expression?
======================================================================

--- Suite: attr_expr_probe ---
  Parts found: 1 (PartDefinition: 0, PartUsage: 1)
  Part: probe_design (PartUsage)
    length                         : has_expr=True  root=LiteralRational  text=10.0
    width                          : has_expr=True  root=LiteralRational  text=5.0
    height                         : has_expr=True  root=LiteralRational  text=3.0
    rate                           : has_expr=True  root=LiteralRational  text=12.0
    markup                         : has_expr=True  root=LiteralRational  text=1.15
    p_fusion                       : has_expr=True  root=LiteralRational  text=2600.0
    p_input                        : has_expr=True  root=LiteralRational  text=50.0
    eta_thermal                    : has_expr=True  root=LiteralRational  text=0.46
    eta_direct                     : has_expr=True  root=LiteralRational  text=0.85
    m_neutron                      : has_expr=True  root=LiteralRational  text=1.1
    f_pump                         : has_expr=True  root=LiteralRational  text=0.06
    eta_pump                       : has_expr=True  root=LiteralRational  text=0.5
    f_subsystem                    : has_expr=True  root=LiteralRational  text=0.03
    r_inner                        : has_expr=True  root=LiteralRational  text=4.2
    r_outer                        : has_expr=True  root=LiteralRational  text=4.4
    r_major                        : has_expr=True  root=LiteralRational  text=3.0
    kappa                          : has_expr=True  root=LiteralRational  text=3.0
    area                           : has_expr=True  root=OperatorExpression  text=length * width
    q_scientific                   : has_expr=True  root=OperatorExpression  text=p_fusion / p_input
    total_dim                      : has_expr=True  root=OperatorExpression  text=length + width
    net_length                     : has_expr=True  root=OperatorExpression  text=length - 1.0
    volume                         : has_expr=True  root=OperatorExpression  text=length * width * height
    perimeter                      : has_expr=True  root=OperatorExpression  text=2.0 * length + 2.0 * width
    minor_radius                   : has_expr=True  root=OperatorExpression  text=r_inner + r_outer / 2.0 - r_major
    gross_electric_simple          : has_expr=True  root=OperatorExpression  text=eta_thermal * p_fusion + eta_direct * p_input
    p_alpha                        : has_expr=True  root=OperatorExpression  text=p_fusion * 3.52 / 17.58
    p_neutron                      : has_expr=True  root=OperatorExpression  text=p_fusion * 14.06 / 17.58
    p_blanket_thermal              : has_expr=True  root=OperatorExpression  text=m_neutron * p_fusion + p_input + eta_thermal * f_pump * eta_
    cost                           : has_expr=True  root=OperatorExpression  text=area * rate
    marked_up_cost                 : has_expr=True  root=OperatorExpression  text=cost * markup
    cost_density                   : has_expr=True  root=OperatorExpression  text=cost / volume
    scaled_area                    : has_expr=True  root=OperatorExpression  text=.(scale_calc) * 2.0
    scale_result                   : has_expr=True  root=FeatureChainExpression  text=.(scale_calc)
    half_vol                       : has_expr=True  root=FeatureChainExpression  text=.(split)
    quarter_vol                    : has_expr=True  root=FeatureChainExpression  text=.(split)

  FR-8: API fields on first attribute with expression:
    feature_value_expression       : YES
    name                           : YES
    qualified_name                 : YES
    declared_name                  : YES
    owned_members                  : YES
    heritage                       : YES
    is_abstract                    : YES
    is_derived                     : YES
    is_end                         : YES
    is_ordered                     : YES
    is_unique                      : YES
    is_constant                    : YES
    direction                      : YES
    multiplicity                   : YES
    feature_value                  : YES
    valuation                      : no

  SUMMARY: 35/35 attributes have feature_value_expression
```

```

======================================================================
Q2: Reference Resolution
======================================================================

--- Suite: attr_expr_probe ---
  probe_design.area (FORMULA):
    ref: length                          qname: AttrExprProbeDesign::probe_design::length
    ref: width                           qname: AttrExprProbeDesign::probe_design::width
  probe_design.q_scientific (FORMULA):
    ref: p_fusion                        qname: AttrExprProbeDesign::probe_design::p_fusion
    ref: p_input                         qname: AttrExprProbeDesign::probe_design::p_input
  probe_design.total_dim (FORMULA):
    ref: length                          qname: AttrExprProbeDesign::probe_design::length
    ref: width                           qname: AttrExprProbeDesign::probe_design::width
  probe_design.net_length (FORMULA):
    ref: length                          qname: AttrExprProbeDesign::probe_design::length
  probe_design.volume (FORMULA):
    ref: length                          qname: AttrExprProbeDesign::probe_design::length
    ref: width                           qname: AttrExprProbeDesign::probe_design::width
    ref: height                          qname: AttrExprProbeDesign::probe_design::height
  probe_design.perimeter (FORMULA):
    ref: length                          qname: AttrExprProbeDesign::probe_design::length
    ref: width                           qname: AttrExprProbeDesign::probe_design::width
  probe_design.minor_radius (FORMULA):
    ref: r_inner                         qname: AttrExprProbeDesign::probe_design::r_inner
    ref: r_outer                         qname: AttrExprProbeDesign::probe_design::r_outer
    ref: r_major                         qname: AttrExprProbeDesign::probe_design::r_major
  probe_design.gross_electric_simple (FORMULA):
    ref: eta_thermal                     qname: AttrExprProbeDesign::probe_design::eta_thermal
    ref: p_fusion                        qname: AttrExprProbeDesign::probe_design::p_fusion
    ref: eta_direct                      qname: AttrExprProbeDesign::probe_design::eta_direct
    ref: p_input                         qname: AttrExprProbeDesign::probe_design::p_input
  probe_design.p_alpha (FORMULA):
    ref: p_fusion                        qname: AttrExprProbeDesign::probe_design::p_fusion
  probe_design.p_neutron (FORMULA):
    ref: p_fusion                        qname: AttrExprProbeDesign::probe_design::p_fusion
  probe_design.p_blanket_thermal (FORMULA):
    ref: m_neutron                       qname: AttrExprProbeDesign::probe_design::m_neutron
    ref: p_fusion                        qname: AttrExprProbeDesign::probe_design::p_fusion
    ref: p_input                         qname: AttrExprProbeDesign::probe_design::p_input
    ref: eta_thermal                     qname: AttrExprProbeDesign::probe_design::eta_thermal
    ref: f_pump                          qname: AttrExprProbeDesign::probe_design::f_pump
    ref: eta_pump                        qname: AttrExprProbeDesign::probe_design::eta_pump
    ref: f_subsystem                     qname: AttrExprProbeDesign::probe_design::f_subsystem
    ref: m_neutron                       qname: AttrExprProbeDesign::probe_design::m_neutron
    ref: p_fusion                        qname: AttrExprProbeDesign::probe_design::p_fusion
  probe_design.cost (FORMULA):
    ref: area                            qname: AttrExprProbeDesign::probe_design::area
    ref: rate                            qname: AttrExprProbeDesign::probe_design::rate
  probe_design.marked_up_cost (FORMULA):
    ref: cost                            qname: AttrExprProbeDesign::probe_design::cost
    ref: markup                          qname: AttrExprProbeDesign::probe_design::markup
  probe_design.cost_density (FORMULA):
    ref: cost                            qname: AttrExprProbeDesign::probe_design::cost
    ref: volume                          qname: AttrExprProbeDesign::probe_design::volume
  probe_design.scaled_area (EXPOSE):
    ref: result                          qname: AttrExprProbeLibrary::ScaleCalc::result
    ref: scale_calc                      qname: AttrExprProbeDesign::probe_design::scale_calc
  probe_design.scale_result (EXPOSE):
    ref: result                          qname: AttrExprProbeLibrary::ScaleCalc::result
    ref: scale_calc                      qname: AttrExprProbeDesign::probe_design::scale_calc
  probe_design.half_vol (EXPOSE):
    ref: half                            qname: AttrExprProbeLibrary::SplitCalc::half
    ref: split                           qname: AttrExprProbeDesign::probe_design::split
  probe_design.quarter_vol (EXPOSE):
    ref: quarter                         qname: AttrExprProbeLibrary::SplitCalc::quarter
    ref: split                           qname: AttrExprProbeDesign::probe_design::split
```

```

======================================================================
Q3: EXPOSE Pattern Analysis
======================================================================

--- Suite: attr_expr_probe ---
  probe_design.scaled_area:
    root_node_type: OperatorExpression
    node_types:     ['OperatorExpression', 'FeatureChainExpression', 'FeatureReferenceExpression', 'LiteralRational']
    sysml_text:     .(scale_calc) * 2.0
    refs:           ['result', 'scale_calc']
    ref_qnames:     ['AttrExprProbeLibrary::ScaleCalc::result', 'AttrExprProbeDesign::probe_design::scale_calc']
  probe_design.scale_result:
    root_node_type: FeatureChainExpression
    node_types:     ['FeatureChainExpression', 'FeatureReferenceExpression']
    sysml_text:     .(scale_calc)
    refs:           ['result', 'scale_calc']
    ref_qnames:     ['AttrExprProbeLibrary::ScaleCalc::result', 'AttrExprProbeDesign::probe_design::scale_calc']
  probe_design.half_vol:
    root_node_type: FeatureChainExpression
    node_types:     ['FeatureChainExpression', 'FeatureReferenceExpression']
    sysml_text:     .(split)
    refs:           ['half', 'split']
    ref_qnames:     ['AttrExprProbeLibrary::SplitCalc::half', 'AttrExprProbeDesign::probe_design::split']
  probe_design.quarter_vol:
    root_node_type: FeatureChainExpression
    node_types:     ['FeatureChainExpression', 'FeatureReferenceExpression']
    sysml_text:     .(split)
    refs:           ['quarter', 'split']
    ref_qnames:     ['AttrExprProbeLibrary::SplitCalc::quarter', 'AttrExprProbeDesign::probe_design::split']

  SUMMARY: 4 EXPOSE-pattern attributes found
```

```

======================================================================
Q4: Cross-Part References
======================================================================

--- Suite: attr_expr_probe ---
  No cross-part references detected

  SUMMARY: 0 attributes with dotted references
```

```

======================================================================
Q5: Pattern Inventory
======================================================================
  Suite                     | FORMULA |  EXPOSE | LITERAL | UNRESOLVABLE | MIXED | NO_EXPR | Total
  ------------------------------------------------------------------------------------------------
  attr_expr_probe           |      14 |       4 |      17 |            0 |     0 |       0 |    35
  ------------------------------------------------------------------------------------------------
  TOTAL                     |      14 |       4 |      17 |            0 |     0 |       0 |    35
```

```

======================================================================
Q6: Compiler Reuse -- Phase 1 compiler on attribute expressions
======================================================================

--- Suite: attr_expr_probe ---
  probe_design.length (LITERAL):
    sysml:    10.0
    compiled: 10.0
  probe_design.width (LITERAL):
    sysml:    5.0
    compiled: 5.0
  probe_design.height (LITERAL):
    sysml:    3.0
    compiled: 3.0
  probe_design.rate (LITERAL):
    sysml:    12.0
    compiled: 12.0
  probe_design.markup (LITERAL):
    sysml:    1.15
    compiled: 1.15
  probe_design.p_fusion (LITERAL):
    sysml:    2600.0
    compiled: 2600.0
  probe_design.p_input (LITERAL):
    sysml:    50.0
    compiled: 50.0
  probe_design.eta_thermal (LITERAL):
    sysml:    0.46
    compiled: 0.46
  probe_design.eta_direct (LITERAL):
    sysml:    0.85
    compiled: 0.85
  probe_design.m_neutron (LITERAL):
    sysml:    1.1
    compiled: 1.1
  probe_design.f_pump (LITERAL):
    sysml:    0.06
    compiled: 0.06
  probe_design.eta_pump (LITERAL):
    sysml:    0.5
    compiled: 0.5
  probe_design.f_subsystem (LITERAL):
    sysml:    0.03
    compiled: 0.03
  probe_design.r_inner (LITERAL):
    sysml:    4.2
    compiled: 4.2
  probe_design.r_outer (LITERAL):
    sysml:    4.4
    compiled: 4.4
  probe_design.r_major (LITERAL):
    sysml:    3.0
    compiled: 3.0
  probe_design.kappa (LITERAL):
    sysml:    3.0
    compiled: 3.0
  probe_design.area (FORMULA):
    sysml:    length * width
    compiled: (inputs.length * inputs.width)
  probe_design.q_scientific (FORMULA):
    sysml:    p_fusion / p_input
    compiled: (inputs.p_fusion / inputs.p_input)
  probe_design.total_dim (FORMULA):
    sysml:    length + width
    compiled: (inputs.length + inputs.width)
  probe_design.net_length (FORMULA):
    sysml:    length - 1.0
    compiled: (inputs.length - 1.0)
  probe_design.volume (FORMULA):
    sysml:    length * width * height
    compiled: ((inputs.length * inputs.width) * inputs.height)
  probe_design.perimeter (FORMULA):
    sysml:    2.0 * length + 2.0 * width
    compiled: ((2.0 * inputs.length) + (2.0 * inputs.width))
  probe_design.minor_radius (FORMULA):
    sysml:    r_inner + r_outer / 2.0 - r_major
    compiled: (((inputs.r_inner + inputs.r_outer) / 2.0) - inputs.r_major)
  probe_design.gross_electric_simple (FORMULA):
    sysml:    eta_thermal * p_fusion + eta_direct * p_input
    compiled: ((inputs.eta_thermal * inputs.p_fusion) + (inputs.eta_direct * inputs.p_input))
  probe_design.p_alpha (FORMULA):
    sysml:    p_fusion * 3.52 / 17.58
    compiled: ((inputs.p_fusion * 3.52) / 17.58)
  probe_design.p_neutron (FORMULA):
    sysml:    p_fusion * 14.06 / 17.58
    compiled: ((inputs.p_fusion * 14.06) / 17.58)
  probe_design.p_blanket_thermal (FORMULA):
    sysml:    m_neutron * p_fusion + p_input + eta_thermal * f_pump * eta_pump + f_subsystem * m_neutron * p_fusion
    compiled: (((inputs.m_neutron * inputs.p_fusion) + inputs.p_input) + ((inputs.eta_thermal * ((inputs.f_pump * inputs.eta_pump) + inputs.f_subsystem)) * (inputs.m_neutron * inputs.p_fusion)))
  probe_design.cost (FORMULA):
    sysml:    area * rate
    compiled: (inputs.area * inputs.rate)
  probe_design.marked_up_cost (FORMULA):
    sysml:    cost * markup
    compiled: (inputs.cost * inputs.markup)
  probe_design.cost_density (FORMULA):
    sysml:    cost / volume
    compiled: (inputs.cost / inputs.volume)
  probe_design.scaled_area (EXPOSE):
    sysml:    .(scale_calc) * 2.0
    error:    CompilationError: Cannot compile unsupported node: . (reason: unsupported operator: .)  (expected for EXPOSE)
  probe_design.scale_result (EXPOSE):
    sysml:    .(scale_calc)
    error:    CompilationError: Cannot compile unsupported node: . (reason: unsupported operator: .)  (expected for EXPOSE)

  SUMMARY: 31 compiled successfully, 2 failed
```

```

======================================================================
Q7: Architecture Recommendation
======================================================================

  Findings Summary:
    FORMULA attributes:      14
    EXPOSE attributes:       4
    LITERAL attributes:      17
    UNRESOLVABLE attributes: 0
    Compilation succeeded:   YES

  Architecture Options Analysis:
    Option A (Synthetic CalcDef+CalcUsage):
      Pro: Reuses all existing infrastructure (backtracker, graph builder, templates)
      Con: Heaviest abstraction -- creates phantom SysML elements
      Fit: Good if FORMULA patterns are dominant and CalcDef ceremony is the bottleneck
    Option B (Synthetic CalcUsage only):
      Pro: Lighter than A, still reuses module generation
      Con: Still creates phantom elements, CalcDef still needed
      Fit: Good if a reusable computed-attribute CalcDef can serve many parts
    Option C (Direct graph integration):
      Pro: Cleanest model -- ComputedAttributeData is first-class
      Con: Requires extending graph builder and templates
      Fit: Best if FORMULA + EXPOSE both significant and need different handling
    Option D (Inline @computed_field):
      Pro: Simplest for FORMULA patterns -- no new modules
      Con: Cannot handle EXPOSE (cross-module references)
      Fit: Good only if FORMULA patterns are rare and simple

  RECOMMENDATION:
    [To be finalized based on empirical findings above -- see report.md for full grounded analysis]
```

```

======================================================================
FR-9: Unsupported / Unexpected Node Types
======================================================================
  No unexpected node types encountered.
```

```

======================================================================
GO / NO-GO DECISION
======================================================================

  Gate Criteria:
    1. ASTs available on PartDef attributes:  YES
    2. FORMULA pattern found:                 YES
    3. Phase 1 compiler works for attributes:  YES

  DECISION: GO
    AST availability confirmed and compiler reuse validated.
    Proceed to ATTR-EXPR Item 2.
```
