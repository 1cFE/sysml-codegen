"""Spike: Measure which resolution step resolves each binding.

Purpose: Determine if removing the Key_A fallback (Step 1) in
DependencyBacktracker._resolve_binding_via_registry() is safe.

For each model snapshot, this test:
1. Builds a real OutputRegistry from snapshot data
2. Monkeypatches the backtracker's resolution method to record which step
   resolved each binding (Step 0/1/1b/2/3/4)
3. Runs find_required_modules(include_all=True) on the full model
4. Reports a breakdown of resolution steps

If Step 1 (unscoped Key_A) resolves ZERO bindings across all models,
removing the fallback is safe.

If Step 1 resolves ANY bindings, those bindings need Key_C registration
fixes before the fallback can be removed.
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_mbse.sysml.types import BindingType
from sysml_codegen.analysis.dependency_backtracker import (
    DependencyBacktracker,
)
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.generation.initialization import build_output_registry
from tests.helpers.snapshot_loader import load_extraction_snapshot


logger = logging.getLogger(__name__)


# Models that have extraction snapshots
SNAPSHOT_MODELS = [
    "solar_battery_model",
    "chain_spike_model",
    "catf_mfe_model",
    "attr_expr_probe",
    "sample_model",
    "issue22_model",
]


@dataclass
class ResolutionEvent:
    """One binding resolution, recording which step resolved it."""

    usage_qn: str
    param_name: str
    source_path: str
    binding_type: str
    step: str  # "step0", "step1", "step1b", "step2", "step3", "step4"
    resolved_channel: str | None = None


@dataclass
class ModelResolutionReport:
    """Full resolution report for one model."""

    model_name: str
    events: list[ResolutionEvent] = field(default_factory=list)
    step_counts: Counter = field(default_factory=Counter)

    def summary(self) -> str:
        lines = [f"\n{'='*70}", f"Model: {self.model_name}", f"{'='*70}"]
        total = len(self.events)
        lines.append(f"Total bindings resolved: {total}")
        for step in ["step0", "step1", "step1b", "step2", "step3", "step4", "skipped"]:
            count = self.step_counts[step]
            pct = f"{count/total*100:.1f}%" if total > 0 else "N/A"
            marker = " *** KEY_A FALLBACK ***" if step == "step1" and count > 0 else ""
            lines.append(f"  {step:8s}: {count:4d} ({pct}){marker}")

        # Detail any step1 hits
        step1_events = [e for e in self.events if e.step == "step1"]
        if step1_events:
            lines.append(f"\n  Step 1 (Key_A fallback) details:")
            for e in step1_events:
                lines.append(
                    f"    {e.usage_qn} | {e.param_name}"
                    f"\n      source_path: {e.source_path}"
                    f"\n      binding_type: {e.binding_type}"
                    f"\n      resolved_to: {e.resolved_channel}"
                )
        return "\n".join(lines)


def _build_instrumented_resolver(backtracker: DependencyBacktracker, report: ModelResolutionReport):
    """Return a patched _resolve_binding_via_registry that records resolution steps."""

    original_method = backtracker._resolve_binding_via_registry
    registry = backtracker._output_registry

    def instrumented_resolve(binding, usage):
        source_path = binding.source_path
        param_name = binding.param_name

        # Reproduce the resolution cascade, tracking which step fires
        assert registry is not None
        channel = None
        step = "step4"  # default: fallback

        # Step 0: Scoped resolve
        consumer_scope = backtracker._consumer_scope_dotted(usage)
        if consumer_scope and source_path and "::" not in source_path:
            scoped_key = f"{consumer_scope}.{source_path}"
            ch = registry.resolve(scoped_key)
            if ch is not None:
                channel = ch
                step = "step0"

        # Step 1: Direct registry resolve (unscoped - the Key_A fallback)
        if channel is None:
            ch = registry.resolve(source_path)
            if ch is not None:
                # Check self-reference guard
                producing_usage_qn = ch.rsplit("__", 1)[0] if "__" in ch else ch
                if producing_usage_qn != usage.qualified_name:
                    channel = ch
                    step = "step1"

        # Step 1b: SysML QN normalization
        if channel is None and source_path and "::" in source_path:
            from sysml_codegen.core.qualified_names import sanitize_name
            parts = source_path.split("::")
            if len(parts) >= 2:
                sanitized_part = sanitize_name(parts[-2]).lower()
                dotted = f"{sanitized_part}.{parts[-1]}"
                ch = registry.resolve(dotted)
                if ch is not None:
                    producing_usage_qn = ch.rsplit("__", 1)[0] if "__" in ch else ch
                    if producing_usage_qn != usage.qualified_name:
                        channel = ch
                        step = "step1b"

        # Step 2: REFERENCE secondary
        if channel is None and binding.binding_type == BindingType.REFERENCE:
            ch = backtracker._resolve_reference_via_registry(source_path, usage)
            if ch is not None:
                channel = ch
                step = "step2"

        # Step 3: Design attribute
        if channel is None:
            design_attr_qn = backtracker._resolve_to_design_attribute(source_path, usage)
            if design_attr_qn:
                step = "step3"

        # Step 4: Fallback (already defaulted)

        # For bindings that won't enter _resolve_binding_via_registry
        # (e.g., LITERAL, UNBOUND), track as "skipped"
        bt = getattr(binding, 'binding_type', None)
        if bt in (BindingType.LITERAL, BindingType.UNBOUND):
            step = "skipped"

        event = ResolutionEvent(
            usage_qn=usage.qualified_name,
            param_name=param_name,
            source_path=source_path or "",
            binding_type=str(bt),
            step=step,
            resolved_channel=channel,
        )
        report.events.append(event)
        report.step_counts[step] += 1

        # Call the original method so the backtracker state stays consistent
        return original_method(binding, usage)

    return instrumented_resolve


def _load_and_analyze(model_name: str) -> ModelResolutionReport:
    """Load a model snapshot, run instrumented backtracking, return report."""
    snapshot = load_extraction_snapshot(model_name)

    # Build OutputRegistry
    registry = build_output_registry(
        calc_usages=snapshot["calc_usages"],
        calc_defs=snapshot["calc_defs"],
        aggregation_data=snapshot.get("aggregation_expressions", []),
        computed_attributes=snapshot.get("computed_attributes", []),
        channel_aliases=snapshot.get("channel_aliases", []),
        design_attributes=snapshot.get("design_attributes", {}),
    )

    # Build backtracker
    backtracker = DependencyBacktracker(
        all_usages=snapshot["calc_usages"],
        calc_defs=snapshot["calc_defs"],
        design_attributes=snapshot.get("design_attributes"),
        output_registry=registry,
    )

    # Instrument the resolver
    report = ModelResolutionReport(model_name=model_name)
    instrumented = _build_instrumented_resolver(backtracker, report)
    backtracker._resolve_binding_via_registry = instrumented

    # Run backtracking on all usages
    result = backtracker.find_required_modules([], include_all=True)

    return report


@pytest.mark.parametrize("model_name", SNAPSHOT_MODELS)
def test_key_a_fallback_not_needed(model_name: str):
    """Verify that Step 1 (unscoped Key_A fallback) resolves zero bindings.

    If this test PASSES: removing the fallback is safe for this model.
    If this test FAILS: the failure output shows exactly which bindings
    depend on Key_A, so you know what Key_C registrations to fix.
    """
    report = _load_and_analyze(model_name)
    print(report.summary())

    step1_events = [e for e in report.events if e.step == "step1"]

    assert len(step1_events) == 0, (
        f"Model '{model_name}': {len(step1_events)} binding(s) resolve via "
        f"Step 1 (Key_A fallback). These need Key_C fixes before the fallback "
        f"can be removed:\n"
        + "\n".join(
            f"  - {e.usage_qn}|{e.param_name} -> {e.resolved_channel} "
            f"(source_path='{e.source_path}')"
            for e in step1_events
        )
    )


def test_full_resolution_report():
    """Print a comprehensive resolution report across all models.

    Not an assertion test — just diagnostic output. Run with -s to see it.
    """
    all_step1 = []
    for model_name in SNAPSHOT_MODELS:
        try:
            report = _load_and_analyze(model_name)
            print(report.summary())
            all_step1.extend(
                (model_name, e) for e in report.events if e.step == "step1"
            )
        except Exception as e:
            print(f"\n{'='*70}\nModel: {model_name} — FAILED: {e}\n{'='*70}")

    print(f"\n{'='*70}")
    print(f"TOTAL Step 1 (Key_A fallback) hits across all models: {len(all_step1)}")
    if all_step1:
        print("VERDICT: NOT SAFE to remove fallback without fixing these:")
        for model_name, e in all_step1:
            print(f"  [{model_name}] {e.usage_qn}|{e.param_name} -> {e.resolved_channel}")
    else:
        print("VERDICT: SAFE to remove Key_A fallback — zero bindings depend on it.")
    print(f"{'='*70}")
