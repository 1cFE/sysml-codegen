package AliasAggD5Library {
    doc /*
    Quoted calc-def names plus an aggregation read through a chain alias,
    written in the D-5 binding form.

    This is the exact-route replacement specimen for ``alias_agg_probe``, a
    ratified ``expected-collapse`` row: its ``in base_cost = base_cost``
    binding is an ``SI_SELF_BINDING`` the exact route refuses. Everything the
    probe existed to catch is kept:

      * three quoted calc defs (``'Unit Cost Calc'``, ``'Margin Calc'``,
        ``'Report Calc'``), so every derived module identifier, class name and
        file path has to be sanitized before it reaches a file;
      * an aggregation over an arrayed child (``sum(widget.total_cost)``);
      * a chain alias of that aggregation (``:>> reported_cost = total_cost``);
      * one calc usage reading the aggregation directly and one reading it
        through the alias.

    The only edit against the probe is the binding form: the leaf's cost model
    now binds ``in base_cost_in = base_cost``.

    **Source**: authored for recovery plan Gate 4C, row L-099
    **Reference**: tests/fixtures/alias_agg_probe/library.sysml
    **Last Updated**: 2026-08-11
    */

    private import ScalarValues::Real;
    private import NumericalFunctions::sum;

    calc def 'Unit Cost Calc' {
        doc /*
        Unit cost from a base cost and a markup.

        **Source**: alias_agg_probe's 'Unit Cost Calc', D-5 binding form
        **Reference**: tests/fixtures/alias_agg_probe/library.sysml
        **Last Updated**: 2026-08-11
        */

        in attribute base_cost_in : Real;
        in attribute markup_in : Real default := 1.5;

        out attribute unit_cost : Real = base_cost_in * markup_in;
    }

    calc def 'Margin Calc' {
        doc /*
        Margin from a cost basis. Reads the aggregation directly.

        **Source**: alias_agg_probe's 'Margin Calc'
        **Reference**: tests/fixtures/alias_agg_probe/library.sysml
        **Last Updated**: 2026-08-11
        */

        in attribute cost_basis : Real;
        in attribute margin_rate : Real;

        out attribute margin : Real = cost_basis * margin_rate;
    }

    calc def 'Report Calc' {
        doc /*
        Passthrough. Reads the aggregation through its chain alias.

        **Source**: alias_agg_probe's 'Report Calc'
        **Reference**: tests/fixtures/alias_agg_probe/library.sysml
        **Last Updated**: 2026-08-11
        */

        in attribute cost_input : Real;

        out attribute report_value : Real = cost_input;
    }

    abstract part def 'Costed Item' {
        doc /*
        Two cost attributes: one redefined as an aggregation, one as a chain
        alias of that aggregation.

        **Source**: alias_agg_probe's 'Costed Item'
        **Reference**: tests/fixtures/alias_agg_probe/library.sysml
        **Last Updated**: 2026-08-11
        */

        attribute total_cost : Real;
        attribute reported_cost : Real;
    }

    part def 'Widget' :> 'Costed Item' {
        doc /*
        Leaf part with an embedded cost model, bound in the D-5 form.

        **Source**: alias_agg_probe's 'Widget', D-5 binding form
        **Reference**: tests/fixtures/alias_agg_probe/library.sysml
        **Last Updated**: 2026-08-11
        */

        attribute base_cost : Real;

        calc cost_model : 'Unit Cost Calc' {
            in base_cost_in = base_cost;
        }

        :>> total_cost = cost_model.unit_cost;
    }

    part def 'Widget Assembly' :> 'Costed Item' {
        doc /*
        Aggregation plus chain alias, read by two calc usages.

        **Source**: alias_agg_probe's 'Widget Assembly'
        **Reference**: tests/fixtures/alias_agg_probe/library.sysml
        **Last Updated**: 2026-08-11
        */

        part widget : 'Widget' [3];

        :>> total_cost = sum(widget.total_cost);

        :>> reported_cost = total_cost;

        calc margin_calc : 'Margin Calc' {
            in cost_basis = total_cost;
            in margin_rate = 0.15;
        }

        calc report_calc : 'Report Calc' {
            in cost_input = reported_cost;
        }
    }
}

package AliasAggD5Design {
    doc /*
    The concrete assembly: three widgets, each with the same base cost.

    **Source**: authored for recovery plan Gate 4C, row L-099
    **Reference**: tests/fixtures/alias_agg_probe/design.sysml
    **Last Updated**: 2026-08-11
    */

    private import ScalarValues::Real;
    private import AliasAggD5Library::*;

    part plant {
        part assembly : 'Widget Assembly' {
            :>> widget.base_cost = 50.0;
        }
    }
}
