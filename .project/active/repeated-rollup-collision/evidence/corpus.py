"""Generate every generating fixture root (plus the two expected flips) into OUT/<key>."""
import shutil, sys, tempfile, logging
from pathlib import Path
logging.disable(logging.CRITICAL)
from tests.conftest import FIXTURES_DIR
from tests.helpers.refusal_cases.fixture_classes import FixtureClass, model_roots
from sysml_codegen.cli import GenerationConfig
from sysml_codegen.cli.emit import emit_package
from sysml_codegen.cli.prepare import LiveModels, Refused, load_source, prepare

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
keys = sorted(k for k, v in model_roots().items() if v.fixture_class is FixtureClass.GENERATING)
keys += ["unresolvable_attr_probe", "elab_native_plural_scope"]
for key in sorted(set(keys)):
    root = FIXTURES_DIR / key
    with tempfile.TemporaryDirectory() as tmp:
        config = GenerationConfig(output_path=Path(tmp) / "pkg", models_path=root)
        prepared = prepare(load_source(LiveModels((root,))), config.package_name)
        refused = prepared if isinstance(prepared, Refused) else emit_package(prepared, config)
        dest = out / key.replace("/", "__")
        if refused is not None:
            dest.mkdir(parents=True, exist_ok=True)
            (dest / "REFUSED.txt").write_text(repr([(i.code, i.reason) for i in refused.refusal.items]) + "\n")
        else:
            shutil.copytree(config.output_path, dest)
    print(key, "refused" if refused is not None else "generated", flush=True)
