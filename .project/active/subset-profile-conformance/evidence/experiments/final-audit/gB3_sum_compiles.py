import sys; sys.path.insert(0,"/tmp/audit2a-final/perturb"); from edit import edit
edit("sysml-codegen/src/sysml_codegen/extraction/calc_compat_renderer.py", """        raise CompilationError(
            f"unsupported node: invocation ({node.function_qn})",
            reason=SiteReason.COMPILE_INVOCATION,
        )""", """        return "sum(" + ", ".join(_render(a, input_names, member_names) for a in node.arguments) + ")\"""")
