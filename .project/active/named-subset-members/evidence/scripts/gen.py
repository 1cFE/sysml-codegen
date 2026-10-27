"""Generate one models dir into OUT (prepare + emit_package)."""
import sys, logging, shutil
from pathlib import Path
logging.disable(logging.CRITICAL)
from sysml_codegen.cli import GenerationConfig
from sysml_codegen.cli.emit import emit_package
from sysml_codegen.cli.prepare import LiveModels, Refused, load_source, prepare
root, out = Path(sys.argv[1]), Path(sys.argv[2])
shutil.rmtree(out, ignore_errors=True)
config = GenerationConfig(output_path=out, models_path=root)
prepared = prepare(load_source(LiveModels((root,))), config.package_name)
r = prepared if isinstance(prepared, Refused) else emit_package(prepared, config)
print("REFUSED", [(i.code, i.reason, getattr(i, "detail", None)) for i in r.refusal.items] if r is not None else "", "generated" if r is None else "")
