# 16 -- Computed attributes on the exact route

> **Status: live exact-route behavior.** The retired extraction-time classifier and its
> FORMULA / EXPOSE / tentative-chain taxonomy were deleted on 2026-08-18. It had no
> production caller. Computed attributes are owned by the elaborator described here.

## One value walk, three outcomes

Elaboration walks occurrences and resolves the single declaration that writes each attribute
slot. It then interprets that writer's value expression in `elaboration/elaborate.py`:

| Authored value | Exact graph result |
|---|---|
| literal, enumeration value, or absent | an `AttrNode` carrying the value |
| feature reference or feature chain | an alias `AttrNode`, resolved by exact occurrence identity |
| another supported expression | a computed `CalcNode` carrying compiled `expression_ir` |

There is no classification pass and no tentative state. An alias walk lands on one exact node
or refuses with a located diagnostic. A computed expression becomes complete expression IR or
refuses before a package is generated.

Part-definition aliases expand once per modeled occurrence. Part-usage aliases name their one
modeled occurrence. The public projection is `ComputationGraph.output_aliases`, whose rows carry
instance paths and canonical channels rather than classifier labels.

## Evidence

- `tests/conformance/test_elaboration_computed_attrs.py` proves computed-node lifting,
  formula chaining, and pure aliases.
- `tests/conformance/test_elaboration_expose_shapes.py` proves multi-hop and
  part-definition alias shapes.
- `tests/conformance/test_elaboration_fail_closed.py` proves alias cycles and unsupported
  expressions refuse instead of degrading.
- `tests/integration/test_computed_attributes_exact_route.py` proves generated arithmetic
  matches the model.

The legacy `ComputedAttributeData` and `ComputedAttributeClassification` values remain importable
data-model compatibility surfaces. They do not drive the shipped route.
