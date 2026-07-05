/*
 * Deep Cross-Scope Probe — Library Definitions
 *
 * PURPOSE: Exercise deeply-nested cross-scope REFERENCE bindings (C6 gap).
 * Tests the backtracker's Step 1b normalization with 4+ segment SysML QN paths
 * and deep feature chains (4+ dot levels).
 *
 * EXPECTED FINDINGS:
 * - Step 1b normalization extracts only last 2 segments of QN, losing
 *   intermediate nesting context. Deep QN paths may fail to resolve.
 * - Deep CHAIN bindings (. notation) may work if OutputRegistry keys
 *   include the full dotted path.
 *
 * Created: 2026-02-17
 * Gap: C6 — Deeply-Nested Cross-Scope REFERENCE (Deferred Issue #7)
 */

package DeepCrossScopeProducer {
    private import ScalarValues::Real;

    // ===== Calc Definitions =====

    calc def 'Core Metric' {
        doc /*
        Leaf-level calculation: calibrates a raw sensor reading.

        **Source**: C6 deep cross-scope probe
        **Reference**: PHASE2_AUDIT_ACTIONS.md C6
        **Last Updated**: 2026-02-17
        */

        in attribute input_val : Real;

        out attribute metric_value : Real = input_val * 1.5;
    }

    calc def 'Derived Metric' {
        doc /*
        Mid-level calculation: applies a scaling factor to a base metric.

        **Source**: C6 deep cross-scope probe
        **Reference**: PHASE2_AUDIT_ACTIONS.md C6
        **Last Updated**: 2026-02-17
        */

        in attribute base_metric : Real;
        in attribute factor : Real default := 2.0;

        out attribute derived_value : Real = base_metric * factor;
    }

    // ===== Part Definitions (3-level nesting) =====

    // Level 3 (leaf): Sensor with CalcUsage producing 'metric_value'
    part def 'Sensor' {
        doc /*
        Leaf component with a single CalcUsage. Deepest nesting level.
        The output 'core.metric_value' is the target for cross-scope references.

        **Source**: C6 deep cross-scope probe
        **Reference**: PHASE2_AUDIT_ACTIONS.md C6
        **Last Updated**: 2026-02-17
        */

        attribute reading : Real;

        calc core : 'Core Metric' {
            in input_val = reading;
        }
    }

    // Level 2: Sensor Array, consuming Sensor output
    part def 'Sensor Array' {
        doc /*
        Mid-level container with a Sensor child and its own CalcUsage.
        The CalcUsage binds to the child sensor's output via feature chain.

        **Source**: C6 deep cross-scope probe
        **Reference**: PHASE2_AUDIT_ACTIONS.md C6
        **Last Updated**: 2026-02-17
        */

        part sensor : 'Sensor';

        calc derived : 'Derived Metric' {
            in base_metric = sensor.core.metric_value;
        }
    }

    // Level 1: Monitoring Station (top of producer hierarchy)
    part def 'Monitoring Station' {
        doc /*
        Top-level container. 3 levels of nesting:
        Station > Array > Sensor > CalcUsage.

        **Source**: C6 deep cross-scope probe
        **Reference**: PHASE2_AUDIT_ACTIONS.md C6
        **Last Updated**: 2026-02-17
        */

        part array : 'Sensor Array';

        // Expose mid-level output for direct consumption
        attribute station_output : Real = array.derived.derived_value;
    }
}

package DeepCrossScopeConsumer {
    private import ScalarValues::Real;

    calc def 'Analysis Calc' {
        doc /*
        Consumer calculation: subtracts a baseline from a data point.
        Used by multiple binding patterns in the design.

        **Source**: C6 deep cross-scope probe
        **Reference**: PHASE2_AUDIT_ACTIONS.md C6
        **Last Updated**: 2026-02-17
        */

        in attribute data_point : Real;
        in attribute baseline : Real default := 0.0;

        out attribute analysis_result : Real = data_point - baseline;
    }

    part def 'Analyzer' {
        doc /*
        Consumer part. Design will add CalcUsages with cross-scope bindings.

        **Source**: C6 deep cross-scope probe
        **Reference**: PHASE2_AUDIT_ACTIONS.md C6
        **Last Updated**: 2026-02-17
        */

        attribute baseline_value : Real;
    }
}
