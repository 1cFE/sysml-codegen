# RG-2: String values, today's behavior and the options

Written in Item 2a Phase 4 (2026-10-18). RG-2 is the owner's decision on String policy (`briefs/align.md`). This document does not decide it. Options and the recommendation are `[AGENT]`.

## The short version

The generator treats a String attribute value like any other attribute value, except at one point: where a String has to reach a calculation. There, two paths are refused and one path silently loses the value.

- **Refused:** a String bound to a calc input, in either spelling, and a String literal written in a calc usage binding. All three are refused at projection (`PROJECTION_FAILED` + `SI_RENDERING_COLLISION`).
- **Silent loss:** a calc def input with a String default that the usage leaves unbound. It generates as a `str` entry point with a null default. The model's value never reaches the generated output.
- **Same as a number, where compared:** a String on an instantiated part and a String read by another attribute behave as a Real does in the same position. A String on an uninstantiated template has no numeric control, so that position was not compared (table below).

The contract's `string-value-omission` rule reports every String attribute value `omitted`. That is true, but for the paths compared with a number it is not String-specific: an unconsumed Real value is not in the output either.

## What each path does today

Every row is a stored case (`tests/expectations/subset_profile/cases/<case>.json`), checked live by `test_generator_half.py`.

| Path | String case | What the generator does | Numeric control | Control does |
|---|---|---|---|---|
| Declared value on an instantiated part, nothing reads it | `string-value-omission__string_value__attribute_value__attribute_declaration`, `…__redefinition_shorthand` | attribute node present (count 1), holding `"liter"`; no entry point | `string-value-omission__unconsumed_numeric_value__attribute_value` | node holds 1.5; no entry point |
| Value on an uninstantiated template | `…__template`, `…__template_shorthand` | no attribute node (count 0); no entry point | none | not compared |
| Read by another attribute | `…__read_by_attribute`, `…__read_by_attribute_shorthand` | source node holds `"liter"`; the reading attribute's value is `None`; no entry point | `string-value-omission__numeric_value__attribute_value__read_by_attribute` | source holds 1.5; reader `None`; no entry point |
| Bound to a calc input | `candidate-es-010-refusal__string_to_calc_input__binding_value` (instance value), `…__attribute_declaration` (declared value) | refused at projection | `string-value-omission__numeric_value__attribute_value` | generates; entry point `fx__gen__fuel_code` |
| String literal in a calc usage binding | `candidate-es-010-refusal__string_usage_literal__binding_value` | refused at projection | none | not compared |
| Calc def String default, input left unbound | `candidate-es-010-refusal__string_library_default__unbound_input` | generates; entry point `fx__gen__t__u`, type `str`, default `null` | `candidate-es-010-refusal__real_library_default__unbound_input` | entry point `fx__gen__t__u`, type `float`, default 3.0 |

The library-default case carries the loss block (family `es-010-string`, disposition `rg2_pending`). The other String cases carry none, because their seams match their numeric controls: there is no String-specific loss to mark.

### The library-default loss in the generated package

Generated from the case model into a scratch directory:

- `schemas/fx_params.py`: `fx__gen__t__u: str = Field(description="Entry point: u")`, a required field with no default.
- `inputs/fx_params.json`: `"fx__gen__t__u": null`.
- `pipelines/pipeline.yaml`: `u: str fx_params.fx__gen__t__u`.

So the model's `"liter"` appears nowhere in the package. A user who runs the input template as generated gets `null` for a required `str` field, which Pydantic rejects; a user who fills it in supplies a value the model already had. I did not run the generated pipeline; the Pydantic behavior is its standard handling of `None` for a `str` field.

### What corrects an earlier premise

Design § D expected a String declaration to leave "no instance-graph attribute node and no entry point", with a numeric control where "both are present". Phase 2 found the node is present (`plan.md` P2.2 notes, the premise conflict). Phase 4 closes it: the node holds the String value, and the missing entry point is what any unconsumed attribute gets. The String-specific behavior is only at the calculation boundary, in the last three rows above.

## Options

**A. Keep today's behavior, and document it.** The refusals stay, and the library default stays a null `str` entry point.
- Generated output: unchanged.
- Consumers: a model with an unbound String default produces an input template that fails validation until a user types in a value the model already had. Nothing says why.
- Cost: none now. The silent loss stays.

**B. Refuse the library-default path too, with its own reason.** A calc input whose only value is a String default becomes a refusal, like the binding paths.
- Generated output: such models stop generating. Models without one are unchanged.
- Consumers: no package with a null String parameter. The modeller is told to bind the input or drop the String.
- Cost: one refusal site and a `SiteReason`. This is also an RG-1 change, because it changes what is accepted.

**C. Carry String values into calculations.** A String bound to a calc input or used as a default becomes a `str` entry point holding its value.
- Generated output: new `str` fields with values in the schemas and input JSON; models refused today start generating.
- Consumers: generated module wrappers and handwritten stencils receive strings. Today's numeric pipeline gives them nothing to do with a string except pass it through, and I did not check whether TEAx modules accept non-numeric inputs.
- Cost: projection, schema and template work, plus a policy for String values reaching numeric code. This is the largest option, and also changes acceptance (RG-1).

**D. Fill the library default but keep refusing bindings.** The unbound String default becomes a `str` entry point with `"liter"` as its default; the binding paths stay refused.
- Generated output: the input template holds the model's value.
- Consumers: the run works without user input, and the value reaches the stencil.
- Cost: small, at the point where projection mints library-default entry points. It leaves an asymmetry: a String reaches a calc through a default but not through a binding. It does not change acceptance.

## Recommendation

**B**, with **D** as the alternative if the owner wants String inputs to work at all.

B closes the only silent loss and makes the three String-to-calculation paths consistent: all refused, each with a reason. It costs one site. D is cheaper in acceptance terms (no RG-1 change) but makes the default path more capable than the binding path, which is harder to explain to a modeller than "Strings do not reach calculations". C should wait for a model that needs String inputs; nothing in the corpus does.

Either way, the contract's `string-value-omission` rule could be narrowed so it reports the calculation boundary rather than every String value. That is a record change in agentic-mbse and is left for the owner's decision here.

## Not checked

- What a TEAx module does when given a `str` input (option C).
- A numeric control for the uninstantiated-template and usage-literal paths.
- SysIDE's own diagnostics on any String model.
