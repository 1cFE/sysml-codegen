"""One-off, reviewed as a diff: the final-audit edits to the hand-kept disagreement record."""
import json, re

P = 'tests/expectations/subset_profile/disagreements.json'
text = open(P).read()
ROW = (" Screen-side rule candidate: agentic-mbse backlog [SUBSET-PROFILE-TYPING-AND-LITERAL-CANDIDATES],"
       " routed to EXEC-SUBSET-CONTRACT Item 3.")
HOME = (" The case lives in codegen's home (D14), not agentic-mbse's package: the records cannot cite it"
        " for the refused pair, because a cited refused case must show the mapped code"
        " (SI_CONSTRAINT_BLOCKED) and this one does not.")

def block(subject):
    start = text.index(f'"subject": "{subject}"')
    start = text.rindex('{', 0, start)
    end = text.index('\n    }', start) + len('\n    }')
    return start, end

def edit(subject, *, reason=None, append=None, resolution=None, rg1=None):
    global text
    s, e = block(subject)
    b = text[s:e]
    m = re.search(r'\n      "reason": (".*")\n', b)
    old_reason = json.loads(m.group(1))
    new_reason = reason if reason is not None else old_reason + append
    assert ROW not in old_reason
    b = b[:m.start(1)] + json.dumps(new_reason, ensure_ascii=False) + b[m.end(1):]
    if resolution is not None:
        b, n = re.subn(r'"resolution": "[a-z0-9_]+"', f'"resolution": "{resolution}"', b)
        assert n == 1
    if rg1 is not None:
        b = b.replace(f'"resolution": "{resolution}",', f'"resolution": "{resolution}",\n      "rg1": "{rg1}",', 1)
    text = text[:s] + b + text[e:]

# Blocker 1: the three entries whose reasons were stale.
edit("case:blocked-predicate-unmapped-code__untyped_assert", reason=(
    "`assert constraint bare;` (an untyped asserted constraint): the screen refuses it as blocked_predicate; "
    "the generator refuses SI_EDGE_DANGLING at constraint association (elaborate.py "
    "_index_constraint_associations, reason elaboration_constraint_definition_unindexed), because the shared "
    "constraint profile selects a library constraint definition codegen does not index. Both refuse, with codes "
    "that do not map: REASON_MAPPING maps blocked_predicate to SI_CONSTRAINT_BLOCKED, and a site reason does not "
    "change that. Not narrowed (the screen would go silent on a refused model) and not RG-1 (the generator fails "
    "closed)." + HOME + ROW))
edit("case:blocked-predicate-unmapped-code__constraint_check_typed", reason=(
    "A `Constraints::ConstraintCheck`-typed constraint: the screen refuses it as blocked_predicate; the generator "
    "refuses SI_EDGE_DANGLING at constraint association (elaborate.py _index_constraint_associations, reason "
    "elaboration_constraint_definition_unindexed), because the shared constraint profile selects the library "
    "definition, which codegen does not index. Both refuse; narrowing the rule would make the screen silent on a "
    "refused model, so the contract is not narrowed. The generator fails closed, so not RG-1. A site reason does "
    "not map the pair, because REASON_MAPPING maps blocked_predicate to SI_CONSTRAINT_BLOCKED." + HOME + ROW))
edit("case:candidate-es-002__part_inside_item_usage__attribute_value", resolution="rg1_pending", rg1="RG1-12", reason=(
    "ES-002 boundary (P5): reading it.rk.cap, an attribute of a part nested in an item usage. Graph validation "
    "refuses SI_EDGE_DANGLING (graph.py _validate_occurrences, reason graph_root_occurrence_package_missing): "
    "codegen makes a part usage owned by an item a root occurrence (occurrence.py:935-942) but gives package "
    "metadata only to a package-owned root. The model is well formed (evidence/semantics-checks.md RG1-12), so "
    "this is a suspected generator defect, not a reproduced gap, and accepting it is the owner's RG-1 call "
    "(rg1-recommendations.md RG1-12; sysml-codegen backlog [ITEM-OWNED-PART-REFUSED]). The run also fires the "
    "ES-002 containment-anchor site (occurrence.py build_containment_address), whose refusal is caught before "
    "graph validation."))

# Advisory 2 (audit numbering; brief item 4): mislabelled entries.
edit("fixture:non_finite_literal", resolution="reproduced_gap", reason=(
    "A non-finite numeric literal (`inf`) is refused EXTRACTION_DIAGNOSTIC_BLOCKING. The blocking diagnostic is "
    "agentic-mbse's shared extraction fact (constraint_extraction.py _literal_node, graded blocking in "
    "constraint_facts.py EXTRACTION_DIAGNOSTIC_SEVERITY), which codegen relays (extraction_screen.py), not a "
    "codegen output policy. The refusal carries no codegen site reason; the diagnostic kind non_finite_literal "
    "names it. The contract reports nothing." + ROW))
edit("fixture:elab_namespace_distinguishability_probe", resolution="reproduced_gap", reason=(
    "An owned member shadows an inherited one with no `:>>` redefinition (`array`, `sensor`), so SysIDE reports a "
    "namespace-distinguishability violation, a language-level check. Codegen promotes it to "
    "SYSML_NAMESPACE_NOT_DISTINGUISHABLE (elaborate.py _blocking_model_validation_diagnostics, role "
    "malformed_input); it is not output naming. The refusal carries no codegen site reason. The contract does not "
    "read SysIDE validation diagnostics, so it is silent."))
edit("fixture:item4_require", reason=(
    "A `require constraint` inside a requirement def reads `w.cost`, a feature of the requirement's subject, which "
    "has no exact live declaration: elaboration refuses SI_EDGE_DANGLING with reason "
    "elaboration_feature_declaration_unindexed (elaborate.py _feature_python_type, the site ES-011 also reaches). "
    "No rule recognizes the construct."))
edit("fixture:elab_constraint_formal_identity", reason=(
    "The constraint def's formal is the quoted name 'max power', which sanitizes to a different public spelling. "
    "The predicate and the wrapper module render the same formal to different binding names, so constraint "
    "name-safety refuses it (CONSTRAINT_NAME_UNSAFE, kind cross_scope_binding_disagreement). It is a disagreement "
    "between two renderings of one name, not a collision between two names. Name safety of generated bindings is "
    "codegen's output fact, which the contract does not model."))
ES010 = (" The screen reports the String value omitted (string-value-omission/string_value, attribute_value), "
         "which is wrong on this path, because the generator refuses at projection (reason "
         "projection_default_non_numeric). Spec § R3 rows closes the ES-010 refusal side as a reproduced gap with "
         "a codegen-owned reason. Policy is RG-2.")
edit("case:candidate-es-010-refusal__string_to_calc_input__binding_value", resolution="reproduced_gap", reason=(
    "A String value bound to a calc input is refused at projection. Entry-point membership is an output fact "
    "codegen owns (ADR 0007), so no shared rule can decide the refusal." + ES010))
edit("case:candidate-es-010-refusal__string_to_calc_input__binding_value__attribute_declaration",
     resolution="reproduced_gap", reason=(
    "The declaration spelling of the String-to-calc-input path (`attribute fuel_unit : String = \"liter\"` bound to "
    "`in u`) is refused at projection exactly as the instance-valued spelling is. Entry-point membership is an "
    "output fact codegen owns (ADR 0007), so no shared rule can decide the refusal." + ES010))
edit("case:candidate-es-010-refusal__string_usage_literal__binding_value", resolution="reproduced_gap", reason=(
    "ES-010 usage-literal path: a String literal written in a calc usage binding is refused at projection (reason "
    "projection_default_non_numeric); the screen reports nothing on this path. Entry-point membership is an "
    "output fact codegen owns (ADR 0007), so no shared rule can decide the refusal. Spec § R3 rows closes the "
    "ES-010 refusal side as a reproduced gap with a codegen-owned reason. The library-default path generates "
    "(codegen-home control). Policy is RG-2."))

# Advisory 1 (audit numbering; brief item 3): point the screen-rule candidates at their backlog row.
for subject in [
    "fixture:plant_value_shapes", "fixture:feature_typing_integrity",
    "case:calc-def-parameter__untyped", "case:calc-def-parameter__quantity_typed",
    "case:feature-type__untyped_attribute", "case:feature-type__subsetting_without_typing",
    "case:feature-type__quantity_value",
    "case:calc-usage-typing__untyped", "case:calc-usage-typing__subsetting_only",
    "case:calc-usage-typing__library_calc_def",
    "case:constraint-typing__inherited_by_subsetting", "case:constraint-typing__untyped_with_bound_input",
    "case:part-typing__two_definitions",
    "case:literal-binding__null", "case:literal-binding__unbounded",
    "case:blocked-predicate-unmapped-code__quantity_operands_mixed_units",
    "case:blocked-predicate-unmapped-code__quantity_operands_same_units",
]:
    edit(subject, append=ROW)

# Advisory 3 (audit numbering; brief item 5): say who decided.
text = text.replace('"schema": "subset-disagreements/1",\n',
                    '"schema": "subset-disagreements/2",\n  "resolutions_decided_by": "agent",\n', 1)
open(P, 'w').write(text)
d = json.loads(text)
print(len(d['entries']), sum(ROW in e['reason'] for e in d['entries']))
