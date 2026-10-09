"""Byte-faithful public generation evidence; expectations are captured separately."""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from sysml_codegen.cli import GenerationConfig, run_codegen


def tree_sha256(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob('*')) if path.is_file()}


def public_result(snapshot: Path, output: Path) -> dict[str, object]:
    records: list[str] = []

    class Refusals(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            if record.levelno >= logging.ERROR:
                records.append(record.getMessage().replace(str(snapshot), '<snapshot>'))

    handler = Refusals()
    logger = logging.getLogger('sysml_codegen')
    logger.addHandler(handler)
    try:
        success = run_codegen(GenerationConfig(output_path=output, from_snapshot=snapshot,
                                               package_name='oracle_package', overwrite=True))
    finally:
        logger.removeHandler(handler)
    return {'success': success, 'refusal': records if not success else [],
            'files': tree_sha256(output) if success else {}}
