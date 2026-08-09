/*
 * Deep Cross-Scope Probe — Design Instance
 *
 * PURPOSE: Exercise deeply-nested cross-scope bindings with three patterns:
 *
 * Pattern A — Deep CHAIN (4-level dot chain):
 *   `station.array.derived_calc.derived_value`
 *   Expected: BindingType.CHAIN, source_path = "station.array.derived_calc.derived_value"
 *   Tests: Deep dotted path resolution through scoped_lookup()
 *
 * Pattern B — Deep REFERENCE (6-segment QN with ::):
 *   `measurement_system::station::array::sensor::core::metric_value`
 *   Expected: BindingType.REFERENCE and an exact producer-output edge to the one concrete core.
 *   Tests: Exact referent identity plus the consumer occurrence selects the producer without
 *   reconstructing the authored qualifier text.
 *
 * Pattern C — Shallow REFERENCE (2-segment self-ref, control):
 *   `analyzer::baseline_value`
 *   Expected: BindingType.REFERENCE, source_path = "...::analyzer::baseline_value"
 *   Tests: Baseline — this pattern works in catf_mfe (catf_physics::p_fusion)
 *
 * EXPECTED OUTCOMES:
 * - Pattern A: Resolves to derived_calc.derived_value.
 * - Pattern B: Resolves to sensor.core.metric_value.
 * - Pattern C: Resolves to analyzer.baseline_value.
 *
 * Created: 2026-02-17
 * Gap: C6 — Deeply-Nested Cross-Scope REFERENCE (Deferred Issue #7)
 */

package DeepCrossScopeDesign {
    private import ScalarValues::Real;
    private import DeepCrossScopeProducer::*;
    private import DeepCrossScopeConsumer::*;

    part measurement_system {
        doc /*
        Top-level design instance containing both producer and consumer hierarchies.

        Producer nesting: measurement_system > station > array > sensor > core
        Consumer: measurement_system > analyzer > {chain_analysis, ref_analysis, self_ref_analysis}

        **Source**: C6 deep cross-scope probe
        **Reference**: PHASE2_AUDIT_ACTIONS.md C6
        **Last Updated**: 2026-02-17
        */

        // ===== Producer Side: 3-level deep hierarchy =====
        part station : 'Monitoring Station' {
            part :>> array : 'Sensor Array' {
                part :>> sensor : 'Sensor' {
                    :>> reading = 10.0;
                }
            }
        }

        // ===== Consumer Side =====
        part analyzer : 'Analyzer' {
            :>> baseline_value = 2.0;

            // --- Pattern A: Deep CHAIN (dot notation, 4 levels deep) ---
            // Accesses: station > array > derived_calc (calc) > derived_value (output)
            // Expected BindingType: CHAIN
            // Expected source_path: "station.array.derived_calc.derived_value"
            calc chain_analysis : 'Analysis Calc' {
                in data_point = station.array.derived_calc.derived_value;
                in baseline = baseline_value;
            }

            // --- Pattern B: Deep REFERENCE (:: notation, 6 segments) ---
            // Accesses: measurement_system > station > array > sensor > core > metric_value
            // Uses qualified name syntax (::) instead of feature chain (.)
            // Expected BindingType: REFERENCE
            // Expected source_path: "...::measurement_system::station::array::sensor::core::metric_value"
            // Exact projection wires this input to the one concrete core output.
            calc ref_analysis : 'Analysis Calc' {
                in data_point = measurement_system::station::array::sensor::core::metric_value;
                in baseline = baseline_value;
            }

            // --- Pattern C: Shallow REFERENCE (:: notation, 2 segments, control) ---
            // Self-reference via :: to own parent's attribute
            // Same pattern as catf_mfe: catf_physics::p_fusion
            // Expected BindingType: REFERENCE
            // Expected source_path: "...::analyzer::baseline_value"
            calc self_ref_analysis : 'Analysis Calc' {
                in data_point = analyzer::baseline_value;
            }
        }
    }
}
