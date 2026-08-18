# Expected transition ledger

This ledger is the closed allow-list for approved design revision 4. The behavior hashes are
SHA-256 of the exact UTF-8 text printed in the behavior columns below. They identify the semantic
contract independently of fixture serialization. The pre-change measurements remain in
`verification/pre-change-baseline.json` and are not rewritten.

The Phase 1 probe lock is authoritative only at P_seed
`52a03cd2d0a9fdd340b60b16cea79a5b72234b08`. Its probe scripts, SysML/KerML source inventory,
fixture manifest, and verdict chain remain immutable. The recapture batch is a generated output
expectation. It is validated separately and must not be presented as a current member of the
frozen P_seed byte inventory.

## Semantic transitions

| Transition | Old behavior hash | New behavior hash | Exact difference | Proving test | Implementation commit |
|---|---|---|---|---|---|
| A1 | `2bb48350e6b78034858a22a7f058ce7c120af55dfd659ee9c5a90c611bd7f768` | `ba6925f46cc1ad2d5271f4175ada49a126a3d9e4bbd3da7971b81007cf624f99` | nearest, descendant, or sole candidate may answer -> exact containment address in the consumer domain or SI_OCCURRENCE_MISSING or SI_OCCURRENCE_AMBIGUOUS | `tests/conformance/test_occurrence_domain_derivation.py` | `3b97c0dd3fc6de31158df275190b7259b5dbff53` |
| A2 | `52b68e6652c48009ea2009060389c2ba9f2f6759fd244dbccbc748f99487dca8` | `1067c7a7351fbd4c1c3366cf5abbe9af9ae241b1b613f3d0e8fcd2c9b76108fd` | nearest or globally sole calculation may answer -> exact contextual calculation-output producer record or named refusal | `tests/conformance/test_occurrence_calc_domain_derivation.py` | `3b97c0dd3fc6de31158df275190b7259b5dbff53` |
| A3 | `e98c2cca3736dc8c67d84f118b2cf023ec973a5823410cec7636528fce0115ba` | `80faf46c71e9b1a599bf7d0817178a786cb6fffa50ce80a58a5c1f5ce30efd85` | one descendant may answer a definition-owned lineage miss -> lineage-local result or SI_OCCURRENCE_MISSING | `tests/conformance/test_definition_owned_reference_positions.py` | `3b97c0dd3fc6de31158df275190b7259b5dbff53` |
| A4 | `f620e0ddb43ab20a0949244f10e996fe92860bff6240b787a01593cade73b9cc` | `d193cb48d4dbcf8ed8648a77d4ba0af8e6a86fdba3b2de9866661e59083d8e4a` | model root may answer a consumer miss -> direct one-step package-owned no-prefix result; nested no-prefix refusal | `tests/conformance/test_occurrence_domain_derivation.py` | `3b97c0dd3fc6de31158df275190b7259b5dbff53` |
| A5 | `c3ec9a52d2669d33b788e8cd13bc6505d0b7ae979538ea33cfb5ecc310ea28b7` | `d9c157c60db3e2be50e84642c411ac95d7226a0b477900d638947e2d1a49bb62` | an element index is ignored -> pre-graph SI_INDEXED_SOURCE_UNSUPPORTED | `tests/conformance/test_expression_evidence_integrity.py` | `3b97c0dd3fc6de31158df275190b7259b5dbff53` |
| A5a | `e11b24a1820592ed4c4080058a2e2f426b7de5ea7f148d8773dfa17e5e0a76cb` | `6343ea0bd6991e9afb33f193bb00795b1e5a844b5d034ce700e4734fc8de896d` | zero-diagnostic graph; authored index silently rewritten to occurrence zero -> pre-graph SI_INDEXED_SOURCE_UNSUPPORTED naming the authored reference | `tests/conformance/test_expression_evidence_integrity.py::test_indexed_bare_chain_singular_slot_refuses_before_consumers` | `3b97c0dd3fc6de31158df275190b7259b5dbff53` |
| A5b | `19e41d38589f77a554de9ab5002ef08a39bf5bd8fa001b5e9a20f928d129d9e9` | `640155d9f5df4bb6157cd4e5d336040473b310d8971d99c2dbfe620d9b19fe3d` | strict: SI_OCCURRENCE_AMBIGUOUS; lenient: graph with SI_OCCURRENCE_AMBIGUOUS + SI_OCCURRENCE_MISSING -> strict and lenient: pre-graph SI_INDEXED_SOURCE_UNSUPPORTED; lenient graph absent | `tests/conformance/test_expression_evidence_integrity.py::test_indexed_bare_chain_plural_slot_refuses_before_occurrence_resolution` | `3b97c0dd3fc6de31158df275190b7259b5dbff53` |
| A6 | `3813f4f1698bfaf477bf0ca5e069a6310428870b20fe12d13371411a54801c60` | `6d612e7923bacb85e8bb83d0808dbdafbf76ed1e5f69e64f7bcb2ebd09c1d0ab` | an unrelated sole multiplicity writer may answer -> exact owner-domain writer or SI_MULTIPLICITY_UNRESOLVED | `tests/conformance/test_occurrence_multiplicity_authority.py` | `3b97c0dd3fc6de31158df275190b7259b5dbff53` |
| B1-B5 | `707e6f80fd08903f50467e0cb86616a261b3046de5edf0c8e7c1a46b1cd80195` | `c92f93c36358ec57562e81f84e015d9123e56c23be0ed5d8bd513815eed475be` | fallback, partial traversal, name recovery, or qualified-name library filtering continues -> exact semantic evidence and DocumentTier or SI_EVIDENCE_INCOMPLETE | `tests/conformance/test_expression_evidence_integrity.py` | `09fdae1986c81c2a5738e1401bdc78e0ea5fa607` |
| B6/B7 | `ef03ebcac409a65f6b53fb62542183183bda037312cf3c0a24a50c164d6dac10` | `9fc41708887a88a929bd94a1b110d9463e25c1cf5b41c3630bb6355890cd8174` | weak type or skipped redefinition identity may pass -> sole qualified primitive type and exact endpoint family or SI_TYPE_INVALID | `tests/conformance/test_feature_typing_integrity.py` | `38045fda5f1fb4298db12b9ad5dac6f532b331e3` |
| B8 | `8ad985020fdfc257fe284d66ccca901910e9840fede1af8a48974f19c1ec2607` | `2162f7650795ab805458c110304992bf3bec233327f6298a8220dd0cbbe31b03` | a resolved fact without a leaf may be skipped -> real corpus totality retained; a forced missing leaf raises typed evidence error | `tests/conformance/test_semantic_evidence_boundary.py` | `09fdae1986c81c2a5738e1401bdc78e0ea5fa607` |
| B9 | `8383f37fd208a1e0dd8aff18e739eba6ffbf8b9a7baeb99783d62ca31e37f3a9` | `57ae40b9b189644e1cc99e160263c6034854fd45cca9b0e452e37f2946a4cf3b` | unsupported root output warns after mutation may begin -> EXIT_POINT_TYPE_UNSUPPORTED before output mutation with status 1 | `tests/conformance/test_generation_exit_type_preflight.py` | `38045fda5f1fb4298db12b9ad5dac6f532b331e3` |
| B10 | `a6d19bfd194416f14a4ae2170434ac504756740f58a949bffd9244f16a9087d3` | `4e67c23824ba0ff8d4a3bab2f77dc4df4515766962b586a29ed8b1f00664918c` | a sole glob may supply feature source origin -> exact parser source origin only; unreachable glob deleted | `tests/conformance/test_feature_typing_integrity.py` | `38045fda5f1fb4298db12b9ad5dac6f532b331e3` |

## Recaptured output bytes

Commit `09fdae1986c81c2a5738e1401bdc78e0ea5fa607` adopted agentic 0.1.3 and
`semantic-evidence/v1`. The 22 maintained graph rows below changed only
`authority.agentic_mbse_version` (`0.1.2` -> `0.1.3`),
`authority.sysml_codegen_version` (`0.1.0` -> `0.1.1`), and the derived integrity digest. Removing
those three fields produces byte-identical JSON structures. Their current bytes still equal the
4A recapture.

| Snapshot | P_seed SHA-256 | 4A SHA-256 | Current SHA-256 |
|---|---|---|---|
| `tests/fixtures/agg_literal_probe/instance_graph_snapshot.json` | `3e4981e072b011179fdabdece93a0ba842917074fdb69fa0e74469b2c58f47c0` | `5f008b27c85a5292096baf1e37e088db5565077e516dff2cead4c06a3972d921` | `5f008b27c85a5292096baf1e37e088db5565077e516dff2cead4c06a3972d921` |
| `tests/fixtures/attr_expr_probe/instance_graph_snapshot.json` | `293e32caced690d0fb8121dfd6b6de2d23a0123caafc029985c6d519c98aa77e` | `f428aa26291a67356ff9f728322d98cb5b8eb6640a42ef3c1c17027ce51b35ac` | `f428aa26291a67356ff9f728322d98cb5b8eb6640a42ef3c1c17027ce51b35ac` |
| `tests/fixtures/catf_mfe_d5/instance_graph_snapshot.json` | `44bd40f5567611a9d6e8ed3456e8e1c7f22adb6dc35253531e0ad97fb152699a` | `f7b8a577e87b3afb714d02b7d2afd884f6c86200ca440f3732e522a722bb1c73` | `f7b8a577e87b3afb714d02b7d2afd884f6c86200ca440f3732e522a722bb1c73` |
| `tests/fixtures/catf_mfe_gated/instance_graph_snapshot.json` | `e80045e405afec25befe2ea0a22afafe5774006cb71533d2dd18e64889781fa1` | `a1ac0b8ef3e9ecc4b20589a0f1096b2623942b269002135bbfd47c2b079770b8` | `a1ac0b8ef3e9ecc4b20589a0f1096b2623942b269002135bbfd47c2b079770b8` |
| `tests/fixtures/chain_spike_d5/instance_graph_snapshot.json` | `aefe6263f0bba3282f5cffce2426ddfe94259a54935444fcb1bca4ab0342e379` | `64d59bde03ead6793559243ef74cdd9f29db9b808beb41b7c8f92f0ad5f494b8` | `64d59bde03ead6793559243ef74cdd9f29db9b808beb41b7c8f92f0ad5f494b8` |
| `tests/fixtures/constraint_domain_satisfy_calc_def/instance_graph_snapshot.json` | `b7f175a1f19c5dc00bbd3cfdfe2a0340cb3634d10425c26a01d04b2d9e82521e` | `ec1c8f81f8d860b2beb80e2092442debef6b127fa29f90cade0d1fcb39282b22` | `ec1c8f81f8d860b2beb80e2092442debef6b127fa29f90cade0d1fcb39282b22` |
| `tests/fixtures/constraint_inline/instance_graph_snapshot.json` | `09a2c2d23ebf6c1265e645ad7f9a3b73ff967c89d2682c8537dab45954767acc` | `cfdff823f19d8b65301ec6009a53ec8329ce94c91b8110beaff6ff14a8244e4b` | `cfdff823f19d8b65301ec6009a53ec8329ce94c91b8110beaff6ff14a8244e4b` |
| `tests/fixtures/constraint_multi_instance/instance_graph_snapshot.json` | `dd51d3d6c55bc72bf278ea54cbd0c8288476bceaec77e8171365f30b9da3abe4` | `751cef1526fbaf92d17c06f8880b605b0af58c5f2ee9136cc43d7591d32ca2ff` | `751cef1526fbaf92d17c06f8880b605b0af58c5f2ee9136cc43d7591d32ca2ff` |
| `tests/fixtures/constraint_non_numerical/instance_graph_snapshot.json` | `0b77f709f29a661e7d2796d881fbfd9c2720cddc300824dc8dd6f34b5c9261be` | `07e00e9c11ece9f1d0d26bc97efb672913836155c8082d68520c0b0303c77128` | `07e00e9c11ece9f1d0d26bc97efb672913836155c8082d68520c0b0303c77128` |
| `tests/fixtures/constraint_occurrence_demand_overrides_d5/instance_graph_snapshot.json` | `dd42832953c9fb3171ce1933e6ca5d38bc5aa9b0c8dbb06692d16abdb9c606f6` | `49ca2fc9818b50d57a35f47293282e636f054f2610c82deaf1010fada4930bbe` | `49ca2fc9818b50d57a35f47293282e636f054f2610c82deaf1010fada4930bbe` |
| `tests/fixtures/d38_caret/instance_graph_snapshot.json` | `8df3672d1826b2cb6a883b6514853963b98bc06e1fef90cefc33505e447ba927` | `769e4fb54e4cbbff9ab065e5b9a740ad04d8853c78f9058436dd406fe2795bf1` | `769e4fb54e4cbbff9ab065e5b9a740ad04d8853c78f9058436dd406fe2795bf1` |
| `tests/fixtures/deep_cross_scope_probe/instance_graph_snapshot.json` | `1e8274c175349c2415329f057dcabbf683dc476624241ca9bb30b45da278f923` | `e8927d0ebb9b28aafcd7410bbc5122354edc4213468f0b2cb2dfc99aedecc46c` | absent; replaced by the exact A2 refusal below |
| `tests/fixtures/fusion_tea/instance_graph_snapshot.json` | `c91a8bf55720cb18cb70ffd16c1442ef4f6aba3a027eeacf300d76abdc2cacd2` | `7d30e7e6499814f9496818e38e12ba46d3d176da627415cd9a50fd239d0b8bed` | `7d30e7e6499814f9496818e38e12ba46d3d176da627415cd9a50fd239d0b8bed` |
| `tests/fixtures/gate_a_d5/instance_graph_snapshot.json` | `3983d074d9523ead7c581aa84abcb834ea9939a97b9a69be732c59a3eedca84f` | `58efd1061efd165a61f0724cf063af5b3998f773027c167168b73724ef47b678` | `58efd1061efd165a61f0724cf063af5b3998f773027c167168b73724ef47b678` |
| `tests/fixtures/modeled_default_fidelity/instance_graph_snapshot.json` | `2359d062b6a1c13c3400b837ffe94fb63597f46ba411ceffd4f91b20fd0bb1c7` | `c096c9352084b86012ab0b8282caadc91da600b5a352e7b07b2145c02016c39d` | `c096c9352084b86012ab0b8282caadc91da600b5a352e7b07b2145c02016c39d` |
| `tests/fixtures/nested_occurrence_override_probe/instance_graph_snapshot.json` | `3b9e1c30b59072642c6ecf0aae1f58c143c758381a036153b5e46f552335f237` | `d7ac88545d5937e326bb25f2b4c71891ed872f345dffa09248a7d91a0cfd2d16` | `d7ac88545d5937e326bb25f2b4c71891ed872f345dffa09248a7d91a0cfd2d16` |
| `tests/fixtures/quoted_owner_formula/instance_graph_snapshot.json` | `4b92b9183a2e320cbf03ad098727a8eddeadc80358367d31273a25ca60c98971` | `c4a7c2d965390aa1e20dfb66e7f35c86a09e8e1dbd3da3aa1471b048104f7a39` | `c4a7c2d965390aa1e20dfb66e7f35c86a09e8e1dbd3da3aa1471b048104f7a39` |
| `tests/fixtures/retype_model/instance_graph_snapshot.json` | `2d90df17a5b9a71afeb66d7114775826c26219ef33bb5bc9b698cc90cd1ceefb` | `d14f7e2dc1ea10783eb3b2d9ce6eee36390b850e736e79ab1f838922fd6d7d2a` | `d14f7e2dc1ea10783eb3b2d9ce6eee36390b850e736e79ab1f838922fd6d7d2a` |
| `tests/fixtures/sample_model/instance_graph_snapshot.json` | `f168bbffa8c252a84ed7a7ebea117ccc7247e61be68f65f579cd4135495523b5` | `08320b152b6596f4b9e882e8d9704d6839c5fbb8458841325856c18f07567092` | `08320b152b6596f4b9e882e8d9704d6839c5fbb8458841325856c18f07567092` |
| `tests/fixtures/shadowed_reference/instance_graph_snapshot.json` | `1d4da393100ef1b68fc80902a8b50a2a32a9e07e94758ab7709f58940b27393c` | `6e96561b26a9a430155e39a2f4b4b6fd90160d6b450313c1d028b0768951afc7` | `6e96561b26a9a430155e39a2f4b4b6fd90160d6b450313c1d028b0768951afc7` |
| `tests/fixtures/solar_battery_d5/instance_graph_snapshot.json` | `dc53520a94f0cd16742b449b69d06772ac904096cd1afa14ca83af709d973930` | `ef9acba733d587e3f17b6073dab9a5e61dd2b2b7aff43ae0356c1ed8bdfcde95` | `ef9acba733d587e3f17b6073dab9a5e61dd2b2b7aff43ae0356c1ed8bdfcde95` |
| `tests/fixtures/unresolvable_attr_probe/instance_graph_snapshot.json` | `17494c69284e80aa0bd7a675c2dcd8d0f92774aee059bacf3b7d937d49069a4e` | `c77fdabf326825349f92f76ff3fc93542c791eaa4fd8bb8008bd66c6cad72082` | `c77fdabf326825349f92f76ff3fc93542c791eaa4fd8bb8008bd66c6cad72082` |
| `tests/fixtures/wi014_toy/instance_graph_snapshot.json` | `5caf02bca8169c693c364aab817683448dcfb4596e9cd86c11263d3062d82301` | `767bcb5ba7e2109c04e40fdcee0d96eca1ddeecc792df3eb307488123559cf77` | `767bcb5ba7e2109c04e40fdcee0d96eca1ddeecc792df3eb307488123559cf77` |

The remaining 4A output change is
`tests/fixtures/golden/computed_attribute_golden.json`: P_seed
`f203c988928cc642cab24fa110dc85c3ed971917f78f5d9548e6b788a0928e18`, current
`08e61f7b5a35241376f2b44498718e322e8f5ee98e49f4fa7ed6b9a4715fa28e`. Its two changed
classifications are owned by A2/B1-B5: `deep_cross_scope_probe.station_output` and
`ife_plant.magnet_volume_total` both changed from `expose_chain_tentative` to `unresolvable` when
the non-exact chain route was removed. No other golden row changed. The proving test is
`tests/conformance/test_computed_attribute_golden.py`. The agentic evidence implementation behind
the 4A boundary is A_final `1804827cb2cc877b3c0bc74309bd3470fb2ee90b`.

## Batch-manifest transition

`tests/fixtures/v6_recapture_batch/batch.json` has three named identities:

| State | SHA-256 | Captured/refused | Meaning |
|---|---|---|---|
| P_seed | `bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288` | 15/22 | Frozen Phase 1 output expectation; retained in Git history |
| 4A | `79a0ea9f712652a4665deb8304fbb7d4c4529d76d72dbb1097e712aafaddc1b4` | 15/22 | Agentic 0.1.3/API metadata recapture at `09fdae1986c81c2a5738e1401bdc78e0ea5fa607` |
| current | `7f9269781a8938308715229c5be00855490e82b7e54f9cb90939195e3aeefa40` | 14/23 | 4A metadata plus the exact A2 and B6/B7 outcomes below |

The current batch differs semantically from 4A at exactly two records. Each record hash is the
SHA-256 of canonical JSON (`sort_keys=True`, compact separators):

| Fixture | 4A behavior/hash | Current behavior/hash | Owner and proof |
|---|---|---|---|
| `deep_cross_scope_probe` | graph 5 modules/4 entry points/0 constraints/1 alias; `f760121418eadedb603cfd16f58f0cd797d2840bc95d84fd3daf5ccfe9796bb0` | `SI_OCCURRENCE_MISSING`: exact output `0b877fee-e8c8-5472-a0b2-24aebac57e50` has no producer in the consumer domain; `55eedd5d2e6388492b860bb049cbcbaf095fc1a9c7db8537a55b02f0cda2a329` | A2; `tests/conformance/test_occurrence_calc_domain_derivation.py`; `tests/conformance/test_v6_snapshot_inventory.py`; stale snapshot `e8927d0ebb9b28aafcd7410bbc5122354edc4213468f0b2cb2dfc99aedecc46c` is absent |
| `plant_value_shapes` | 2 x `SI_SELF_BINDING`; `f091a6420ea6161576b2c72a5ce3bfac782c07f10b33081f0088fb72b2fe11c3` | `SI_TYPE_INVALID` for unsupported `PlantValueShapesLib::'Wall Kind'` at `root-0/library.sysml:92`; `d11224cb84914f0e5d05a40e43ed4e5d620af1e0b799357e8e4024f6730b9ed3` | B6/B7; `tests/conformance/test_feature_typing_integrity.py` |

The current batch and snapshot bytes are regenerated by `scripts/capture_v6_batch.py --check` and
verified by `verification/capture_baseline.py --check --check-current-batch`. The frozen source
inventory is independently reconstructed from the named P_seed by `verification/capture_baseline.py`.
The earlier Item 8 pre/final inventory JSON remains immutable historical evidence at its 23-path
capture. `tests/conformance/test_v6_snapshot_inventory.py` requires that its one path not tracked at
current HEAD is exactly this A2 deletion and that the current batch carries the named refusal.

The frozen source inventory is also compared with the **current** bytes of all 110 SysML/KerML
sources across all 43 roots. An intentional difference must have exactly one row below naming both
hashes. This current-byte leg covers the six `ADDED_ROOTS` directly; it does not rely on the canonical
batch's output hashes.

## Fixture-source transitions

| File | Frozen P_seed SHA-256 | Current SHA-256 | Owning commit | Reason |
|---|---|---|---|---|
| `tests/fixtures/deep_cross_scope_probe/design.sysml` | `02e39cdd033b1bf062fbdd1d69a61d22a59ea357aefe79e6a4ca05d655542e78` | `45c94431900aa58a50629067dbfed2d3c6c096ede3666dc5648d496d900756ec` | `1ce8638ff62aae4f991890e652fd7ad28a683c28` | Comment-only correction: remove the obsolete wiring claim and name the retained `SI_OCCURRENCE_MISSING` refusal plus `[DEEP-QUALIFIED-OUTPUT-WIRING]`. The authored reference and behavior are unchanged. |

Maintained-output result: byte-identical after excluding the exact rows above. No unexplained
snapshot, golden-output, or batch-record byte remains.

## Verification-code transitions

The probe lock pins six non-fixture rows — five probe scripts and
`verification/capture_baseline.py`. Those are live code, not frozen evidence, so neither the
historical-tree leg nor the current-output leg pins them. They are pinned at their **current**
bytes in the implementation tree, and any difference from their lock-time bytes must be owned by a
named row here. An unowned byte change is a hard failure, and it is the second of D10's two
probe-rerun triggers.

| File | Lock-time SHA-256 | Current SHA-256 | Owning commits | Reason |
|---|---|---|---|---|
| `verification/capture_baseline.py` | `6aef97af31d0d3c644c7a5edbf27540b1aca037a7b146090ea430846f29b6cc3` | `a415364e23e14b4d51cec54538fc0a47dcb9f6725af7f9d80c7c91f2bc0bab7e` | `da4aa78` ("docs: reconcile parser evidence contract"), `46694e2` ("fix verification artifact source inputs"), `891923230653b874822148e49ccb5a93e55459d7` ("fix: verify fixture inventory from history") | The validator evolved with the contract it checks. `da4aa78` reconciled the batch inventory against the exact A2 and B6/B7 outcomes; `46694e2` moved its history and source roots onto the explicit hash-identified manifest; `8919232` makes the frozen source inventory come from its named P_seed tree instead of current fixture bytes, as the three-leg lock requires. The current deep-probe comment can therefore describe the refusal without rewriting or weakening the historical fixture lock. |

The five probe scripts under `.project/active/stop-reinventing-the-parser/probes/` are unchanged
from their lock-time bytes and are pinned there; they have no row because they have no difference.
