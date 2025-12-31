"""Preservation logic and backup functionality for smart regeneration.

This module provides decision logic for determining when to regenerate
implementation stencils and functionality to backup existing implementations
before regeneration.
"""

import shutil
from datetime import datetime
from pathlib import Path

# UPDATED: Import from sysml_codegen package
from sysml_codegen.analysis.signature_extractor import (
    extract_signature_from_impl,
    generate_expected_signature,
)
from sysml_codegen.extraction.data_models import CalculationDefinitionData


def should_regenerate_stencil(
    calc_def: CalculationDefinitionData,
    impl_path: Path,
) -> tuple[bool, str]:
    """Determine if implementation stencil should be regenerated.

    Compares existing implementation signature with expected signature
    to decide whether to preserve or regenerate the implementation.

    Decision logic:
    1. File doesn't exist → regenerate (new module)
    2. Can't parse existing file → regenerate (syntax errors)
    3. Signature unchanged → preserve (no interface change)
    4. Signature changed → regenerate (interface changed)

    Args:
        calc_def: Calculation definition from SysML
        impl_path: Path to existing implementation file

    Returns:
        (should_regenerate, reason) tuple
        - should_regenerate: True if stencil needs regeneration
        - reason: Human-readable explanation for the decision
    """
    # Case 1: File doesn't exist - need to generate
    if not impl_path.exists():
        return True, "New module (file doesn't exist)"

    # Case 2: Extract existing signature
    existing_sig = extract_signature_from_impl(impl_path)
    if existing_sig is None:
        # Could not parse - backup and regenerate to be safe
        return True, "Could not parse existing implementation"

    # Case 3: Generate expected signature from SysML
    expected_sig = generate_expected_signature(calc_def)

    # Case 4: Compare signatures
    if existing_sig.matches(expected_sig):
        return False, "Signature unchanged"
    else:
        return True, "Signature changed (return type or input type differs)"


def backup_implementation(
    impl_path: Path,
    backup_dir: Path,
) -> Path:
    """Backup existing implementation before regeneration.

    Creates timestamped backup in backup directory. This preserves
    handwritten implementation logic before regenerating the stencil
    due to signature changes.

    Args:
        impl_path: Path to implementation file to backup
        backup_dir: Directory to store backups

    Returns:
        Path to created backup file
    """
    # Ensure backup directory exists
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = impl_path.stem  # e.g., 'alphaneutronsplit_impl'
    backup_name = f"{stem}_{timestamp}.py"
    backup_path = backup_dir / backup_name

    # Copy file to backup location (preserves metadata)
    shutil.copy2(impl_path, backup_path)

    return backup_path


__all__ = [
    "backup_implementation",
    "should_regenerate_stencil",
]
