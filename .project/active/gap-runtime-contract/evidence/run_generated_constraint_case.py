"""Execute one generated package case in a fresh, source-asserting process."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--package-name", required=True)
    parser.add_argument("--codegen-root", type=Path, required=True)
    parser.add_argument("--case", choices=("finite", "nonfinite"), required=True)
    args = parser.parse_args()

    from simkit.core.pipeline import execute_pipeline

    import sysml_codegen

    assert (
        Path(sysml_codegen.__file__).resolve().is_relative_to((args.codegen_root / "src").resolve())
    )
    package = importlib.import_module(args.package_name)
    assert Path(package.__file__).resolve().is_relative_to(args.package_root.resolve())

    if args.case == "nonfinite":
        for input_file in (args.package_root / args.package_name / "inputs").glob("*.json"):
            payload = json.loads(input_file.read_text())
            for key, value in payload.items():
                if isinstance(value, (int, float)):
                    payload[key] = float("inf")
            input_file.write_text(json.dumps(payload, indent=2) + "\n")

    registry = getattr(package, f"create_{args.package_name}_registry")()
    pipeline = args.package_root / args.package_name / "pipelines" / "pipeline.yaml"
    result = execute_pipeline(
        pipeline,
        args.package_root / f"run-{args.case}",
        registry=registry,
        custom_schema_types=list(package.CUSTOM_SCHEMA_TYPES),
    )
    evaluations = [value for key, value in result.outputs.items() if key.endswith("__evaluation")]
    assert evaluations
    if args.case == "finite":
        assert all(value.status in {"satisfied", "violated"} for value in evaluations)
    else:
        assert all(value.status == "indeterminate" for value in evaluations)


if __name__ == "__main__":
    main()
