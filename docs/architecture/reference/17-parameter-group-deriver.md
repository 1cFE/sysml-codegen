# Parameter Groups After the Exact Cutover

Parameter groups are presentation data projected from the exact instance graph. They do not
discover producers, reconstruct occurrence scope, or choose semantic identity.

Current owners:

- Exact occurrences and bindings: `src/sysml_codegen/elaboration/`
- Generation projection: `src/sysml_codegen/elaboration/project.py`
- Generated parameter rendering: `src/sysml_codegen/generation/`

The Item 7 cutover tests are the executable contract. Full documentation certification remains
Item 8 work.
