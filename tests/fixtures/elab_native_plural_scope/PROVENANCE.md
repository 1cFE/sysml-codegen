# Provenance: native effective declarations and plural scope

- **[REFERENT]** `.project/active/elaborator-design/design.md`, D3 and “Exact contextualization
  rules,” are the behavior bar: SysIDE's `Usage.usages` chooses effective child declarations;
  codegen adds only finite concrete parent/index contexts; plural references stay inside the
  consumer's permitted occurrence scope.
- **[REFERENT]** `.project/active/spike-syside-occurrence-authority/findings.md` is the observed
  SysIDE 0.8.4 boundary this fixture must continue to match.
- **[EXAMPLE]** `spec_chain_twolevel` supplies the usage-level part retype shape, and
  `elab_finite_expression_multiplicity` supplies the modeled finite multiplicity shape. They
  illustrate syntax only; this fixture is the kept combined assertion surface.

The `plant` usage inherits `shadow` and explicitly redefines `selected`. The selected container
inherits then explicitly redefines `leaf` to a subtype. Both containers instantiate the same
base containment slot twice, while each inherited `total = sum(leaf.value)` expression may consume
only its own two concrete leaves. The `Observe` binding also keeps one parser-materialized implied
formal redefinition in the same model.
