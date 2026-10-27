"""Generate every model root (both classes) into OUT/<key>; refusals record codes/reasons."""
import shutil, sys, tempfile, logging, traceback
from pathlib import Path
logging.disable(logging.CRITICAL)
from tests.conftest import FIXTURES_DIR
from tests.helpers.refusal_cases.fixture_classes import model_roots
from sysml_codegen.cli import GenerationConfig
from sysml_codegen.cli.emit import emit_package
from sysml_codegen.cli.prepare import LiveModels, Refused, load_source, prepare

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
keys = sorted(set(model_roots()) | {"unresolvable_attr_probe", "elab_native_plural_scope"})
for key in keys:
    root = FIXTURES_DIR / key
    dest = out / key.replace("/", "__")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            config = GenerationConfig(output_path=Path(tmp) / "pkg", models_path=root)
            prepared = prepare(load_source(LiveModels((root,))), config.package_name)
            refused = prepared if isinstance(prepared, Refused) else emit_package(prepared, config)
            if refused is not None:
                dest.mkdir(parents=True, exist_ok=True)
                (dest / "REFUSED.txt").write_text(repr([(i.code, i.reason) for i in refused.refusal.items]) + "\n")
                st = "refused"
            else:
                shutil.copytree(config.output_path, dest); st = "generated"
    except Exception as e:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "CRASH.txt").write_text(f"{type(e).__name__}: {e}\n"); st = "crash"
    print(key, st, flush=True)
