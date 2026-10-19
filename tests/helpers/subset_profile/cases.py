"""The subset-profile conformance cases: stored answers, the case store, agreement and the record.

A case is one small model with two stored answers (EXEC-SUBSET-CONTRACT Item 2a design D1, D14):

- the generator's, ``tests/expectations/subset_profile/cases/<case_id>.json``, which every case
  has wherever its model lives;
- the screen's, which lives with the model. A case agentic-mbse tests the screen on is
  agentic-mbse package data (``agentic_mbse/sysml/subset_cases/<case_id>/``, read through
  ``agentic_mbse.sysml.conformance_case``); a case only codegen needs keeps its model under
  ``tests/fixtures/subset_profile/<case_id>/`` and its screen answer and construct in its
  stored generator answer.

Agreement (design § C) is one rule for every subject. With C the generator's codes and M the
codes the mapping gives the screen's ``refused`` findings: a run that generated agrees when the
screen refuses nothing; a run that refused agrees when some code in M is in C. Anything else is
a disagreement, and a disagreement passes only if the hand-edited record lists it (D3). This
module is the record's only reader, and it writes nothing.

Everything here is pure: it reads stored files, the packaged records and the mapping.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.conformance_case import (
    Construct,
    ScreenAnswer,
    ScreenFinding,
    load_packaged_case,
    packaged_case_dir,
    packaged_case_ids,
    screen_answer_from_json,
)
from agentic_mbse.sysml.subset_profile import PACKAGED_RULES, Outcome, RuleRecords

from sysml_codegen.elaboration.diagnostics import SiteReason
from sysml_codegen.subset_profile_adapter import REASON_MAPPING, NoRefusal

_TESTS = Path(__file__).resolve().parents[2]
EXPECTATIONS_DIR = _TESTS / "expectations" / "subset_profile"
ANSWERS_DIR = EXPECTATIONS_DIR / "cases"
DISAGREEMENTS_PATH = EXPECTATIONS_DIR / "disagreements.json"
#: Codegen-home case models (design D14). A model collection, not one model.
CODEGEN_CASES_DIR = _TESTS / "fixtures" / "subset_profile"

_RG1_ID = re.compile(r"RG1-[1-9][0-9]*")


class CaseAnswerError(ValueError):
    """A stored answer or the disagreement record does not have its stored form."""


class CaseHome(StrEnum):
    #: The model and screen answer are agentic-mbse package data.
    AGENTIC = "agentic"
    #: The model and screen answer live in this repository.
    CODEGEN = "codegen"


class GeneratorOutcome(StrEnum):
    GENERATED = "generated"
    REFUSED = "refused"


class SeamKind(StrEnum):
    GRAPH_ATTR = "graph_attr"
    ATTR_VALUE = "attr_value"
    ENTRY_POINT = "entry_point"
    CONTRACT_PARAMETER = "contract_parameter"
    CATALOG_USAGE = "catalog_usage"
    CALC_COMPILABILITY = "calc_compilability"
    OCCURRENCES = "occurrences"


class LossDisposition(StrEnum):
    """What a silent loss is today (design D10)."""

    #: The generator leaves the construct out by design, and the contract says so.
    ACCEPTED_OMISSION = "accepted_omission"
    #: A loss that should block, pending the owner's RG-1 decision.
    CANDIDATE_REFUSAL = "candidate_refusal"
    #: A String loss: the policy is the owner's RG-2 decision, so it is neither of the above.
    RG2_PENDING = "rg2_pending"


class DisagreementKind(StrEnum):
    GENERATOR_REFUSES_SCREEN_SILENT = "generator_refuses_screen_silent"
    SCREEN_REFUSES_GENERATOR_BUILDS = "screen_refuses_generator_builds"
    CODE_UNMAPPED = "code_unmapped"


class Decider(StrEnum):
    """Who assigned the record's resolutions. An entry's ``owner`` is who is accountable."""

    #: The implementing agent assigned every resolution, by family; the owner has not ratified
    #: them, so none is an owner ruling.
    AGENT = "agent"
    #: The owner ratified every resolution (RG-3).
    OWNER = "owner"


class Resolution(StrEnum):
    #: The generator's refusal is an output fact codegen owns; no shared rule can describe it.
    CODEGEN_OWNED = "codegen_owned"
    #: A refusal family with no rule: reproduced, with a stable codegen reason.
    REPRODUCED_GAP = "reproduced_gap"
    #: The generator side is an owner decision (RG-1); the entry names its recommendation.
    RG1_PENDING = "rg1_pending"
    #: String policy, the owner's (RG-2).
    RG2_PENDING = "rg2_pending"


@dataclass(frozen=True)
class GeneratorRun:
    """What one live run of the generator determines: the part of the answer capture writes."""

    outcome: GeneratorOutcome
    #: The sorted multiset of elaboration and generation codes.
    codes: tuple[str, ...]
    #: The sorted multiset of the site reasons the refusal carried.
    reasons: tuple[SiteReason, ...]


@dataclass(frozen=True)
class StubAnswer:
    """One calc def member compiled to a ``MANUAL_REQUIRED`` stub, as its notice names it."""

    #: ``<calc def qualified name>::<member name>``.
    output: str
    reason: SiteReason


@dataclass(frozen=True)
class SeamAnswer:
    kind: SeamKind
    declaration: str
    expect: Any


@dataclass(frozen=True)
class GeneratorAnswer:
    run: GeneratorRun
    witnesses: tuple[str, ...]
    stubs: tuple[StubAnswer, ...]
    seams: tuple[SeamAnswer, ...]


@dataclass(frozen=True)
class LossAnswer:
    family: str
    disposition: LossDisposition
    rg1: str | None
    #: The case where the carried form is present at the same seams (spec criterion D1).
    control: str


@dataclass(frozen=True)
class CodegenCase:
    """The parts of a codegen-home case that an agentic-home case keeps in ``case.json``."""

    construct: Construct
    screen: ScreenAnswer


@dataclass(frozen=True)
class StoredAnswer:
    case_id: str
    home: CaseHome
    generator: GeneratorAnswer
    #: Present exactly for codegen-home cases.
    codegen: CodegenCase | None
    loss: LossAnswer | None

    @property
    def subject(self) -> str:
        return f"case:{self.case_id}"


@dataclass(frozen=True)
class Disagreement:
    """A computed disagreement, keyed as the record keys its entries (design D3)."""

    subject: str
    kind: DisagreementKind
    generator_codes: tuple[str, ...]
    #: Sorted reasons of the screen's ``refused`` findings.
    screen_reasons: tuple[str, ...]


@dataclass(frozen=True)
class DisagreementEntry:
    disagreement: Disagreement
    resolution: Resolution
    r3_row: str | None
    #: The person accountable for the disagreement until it closes (spec § Problem's
    #: "recorded disagreement"). A work item or phase is not an owner: it ends, the entry may not.
    #: Accountable is not decided: who assigned the resolution is the record's
    #: ``resolutions_decided_by`` (``resolutions_decided_by()``).
    owner: str
    reason: str
    rg1: str | None


# ---- reading ----------------------------------------------------------------------------------


def _fields(
    value: Any,
    where: str,
    *,
    required: frozenset[str],
    optional: frozenset[str] = frozenset(),
) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise CaseAnswerError(f"{where}: expected an object, got {type(value).__name__}")
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing or unknown:
        raise CaseAnswerError(f"{where}: missing {sorted(missing)}, unknown {sorted(unknown)}")
    return value


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CaseAnswerError(f"{where}: expected a non-empty string, got {value!r}")
    return value


def _list(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise CaseAnswerError(f"{where}: expected a list, got {type(value).__name__}")
    return value


def _texts(value: Any, where: str) -> tuple[str, ...]:
    return tuple(_text(item, f"{where}[{i}]") for i, item in enumerate(_list(value, where)))


def _sorted_texts(value: Any, where: str) -> tuple[str, ...]:
    texts = _texts(value, where)
    if list(texts) != sorted(texts):
        raise CaseAnswerError(f"{where}: must be sorted, got {list(texts)}")
    return texts


def _member[E: StrEnum](enum: type[E], value: Any, where: str) -> E:
    try:
        return enum(value)
    except ValueError:
        raise CaseAnswerError(f"{where}: {value!r} is not a {enum.__name__}") from None


def _rg1(value: Any, where: str) -> str:
    if not (isinstance(value, str) and _RG1_ID.fullmatch(value)):
        raise CaseAnswerError(f"{where}: expected RG1-<n>, got {value!r}")
    return value


def _generator(value: Any, where: str) -> GeneratorAnswer:
    data = _fields(
        value,
        where,
        required=frozenset({"outcome", "codes", "reasons"}),
        optional=frozenset({"witnesses", "stubs", "seams"}),
    )
    outcome = _member(GeneratorOutcome, data["outcome"], f"{where}.outcome")
    codes = _sorted_texts(data["codes"], f"{where}.codes")
    reasons = tuple(
        _member(SiteReason, reason, f"{where}.reasons[{i}]")
        for i, reason in enumerate(_sorted_texts(data["reasons"], f"{where}.reasons"))
    )
    if (outcome is GeneratorOutcome.REFUSED) != bool(codes) or (reasons and not codes):
        raise CaseAnswerError(f"{where}: a refused run has codes, and only a refused run does")
    stubs = []
    for i, item in enumerate(_list(data.get("stubs", []), f"{where}.stubs")):
        stub = _fields(item, f"{where}.stubs[{i}]", required=frozenset({"output", "reason"}))
        stubs.append(
            StubAnswer(
                output=_text(stub["output"], f"{where}.stubs[{i}].output"),
                reason=_member(SiteReason, stub["reason"], f"{where}.stubs[{i}].reason"),
            )
        )
    if stubs != sorted(stubs, key=lambda stub: (stub.output, stub.reason)):
        raise CaseAnswerError(f"{where}.stubs: must be sorted by output, then reason")
    seams = []
    for i, item in enumerate(_list(data.get("seams", []), f"{where}.seams")):
        seam = _fields(
            item, f"{where}.seams[{i}]", required=frozenset({"kind", "declaration", "expect"})
        )
        seams.append(
            SeamAnswer(
                kind=_member(SeamKind, seam["kind"], f"{where}.seams[{i}].kind"),
                declaration=_text(seam["declaration"], f"{where}.seams[{i}].declaration"),
                expect=seam["expect"],
            )
        )
    return GeneratorAnswer(
        run=GeneratorRun(outcome=outcome, codes=codes, reasons=reasons),
        witnesses=_texts(data.get("witnesses", []), f"{where}.witnesses"),
        stubs=tuple(stubs),
        seams=tuple(seams),
    )


def _construct(value: Any, where: str) -> Construct:
    data = _fields(value, where, required=frozenset({"file", "lines", "description"}))
    lines = data["lines"]
    if not (
        isinstance(lines, list)
        and len(lines) == 2
        and all(isinstance(n, int) and n >= 1 for n in lines)
        and lines[0] <= lines[1]
    ):
        raise CaseAnswerError(f"{where}.lines: expected [first, last], got {lines!r}")
    return Construct(
        file=_text(data["file"], f"{where}.file"),
        first_line=lines[0],
        last_line=lines[1],
        description=_text(data["description"], f"{where}.description"),
    )


def _loss(value: Any, where: str) -> LossAnswer:
    data = _fields(
        value,
        where,
        required=frozenset({"family", "disposition", "control"}),
        optional=frozenset({"rg1"}),
    )
    disposition = _member(LossDisposition, data["disposition"], f"{where}.disposition")
    rg1 = None if data.get("rg1") is None else _rg1(data["rg1"], f"{where}.rg1")
    if (disposition is LossDisposition.CANDIDATE_REFUSAL) != (rg1 is not None):
        raise CaseAnswerError(f"{where}: a candidate refusal names its RG1-<n>, and only one does")
    return LossAnswer(
        family=_text(data["family"], f"{where}.family"),
        disposition=disposition,
        rg1=rg1,
        control=_text(data["control"], f"{where}.control"),
    )


def load_stored_answer(path: Path) -> StoredAnswer:
    """Read one stored generator answer, ``<case_id>.json``."""
    where = str(path)
    data = _fields(
        json.loads(path.read_text(encoding="utf-8")),
        where,
        required=frozenset({"id", "home", "generator"}),
        optional=frozenset({"construct", "screen", "loss"}),
    )
    case_id = _text(data["id"], f"{where}.id")
    if case_id != path.stem:
        raise CaseAnswerError(f"{where}: id {case_id!r} is not the file name {path.stem!r}")
    home = _member(CaseHome, data["home"], f"{where}.home")
    local_fields = {"construct", "screen"}
    if local_fields & data.keys() != (local_fields if home is CaseHome.CODEGEN else set()):
        raise CaseAnswerError(
            f"{where}: a construct and a screen answer are stored here exactly for "
            "codegen-home cases"
        )
    codegen = (
        CodegenCase(
            construct=_construct(data["construct"], f"{where}.construct"),
            screen=_screen(data["screen"], f"{where}.screen"),
        )
        if home is CaseHome.CODEGEN
        else None
    )
    return StoredAnswer(
        case_id=case_id,
        home=home,
        generator=_generator(data["generator"], f"{where}.generator"),
        codegen=codegen,
        loss=_loss(data["loss"], f"{where}.loss") if "loss" in data else None,
    )


def _screen(value: Any, where: str) -> ScreenAnswer:
    try:
        return screen_answer_from_json(value, where)
    except ValueError as error:
        raise CaseAnswerError(str(error)) from error


# ---- the case store ---------------------------------------------------------------------------


def answer_ids() -> frozenset[str]:
    """Every case with a stored generator answer."""
    return frozenset(p.stem for p in ANSWERS_DIR.glob("*.json"))


def packaged_ids() -> frozenset[str]:
    """Every case whose model is agentic-mbse package data."""
    return frozenset(packaged_case_ids())


def codegen_ids() -> frozenset[str]:
    """Every case whose model lives in this repository."""
    if not CODEGEN_CASES_DIR.is_dir():
        return frozenset()
    return frozenset(d.name for d in CODEGEN_CASES_DIR.iterdir() if d.is_dir())


def load_answer(case_id: str) -> StoredAnswer:
    return load_stored_answer(ANSWERS_DIR / f"{case_id}.json")


def all_answers() -> tuple[StoredAnswer, ...]:
    return tuple(load_answer(case_id) for case_id in sorted(answer_ids()))


def model_root(answer: StoredAnswer) -> Path:
    """The directory holding the case's model files."""
    if answer.home is CaseHome.AGENTIC:
        return packaged_case_dir(answer.case_id)
    return CODEGEN_CASES_DIR / answer.case_id


def construct_of(answer: StoredAnswer) -> Construct:
    if answer.codegen is not None:
        return answer.codegen.construct
    return load_packaged_case(answer.case_id).construct


def screen_of(answer: StoredAnswer) -> ScreenAnswer:
    """The case's stored screen answer, wherever it lives."""
    if answer.codegen is not None:
        return answer.codegen.screen
    return load_packaged_case(answer.case_id).screen


# ---- agreement (design § C) -------------------------------------------------------------------


def _reason(finding: ScreenFinding, rules: RuleRecords) -> str:
    return rules.rule(finding.rule).shape(finding.shape).reason


def mapped_code(finding: ScreenFinding, rules: RuleRecords = PACKAGED_RULES) -> str:
    """The code the mapping says the generator refuses a ``refused`` finding with."""
    reason = _reason(finding, rules)
    mapping = REASON_MAPPING[reason]
    if isinstance(mapping, NoRefusal):
        raise ValueError(
            f"{finding.rule}/{finding.shape} is refused, but its reason {reason!r} maps to "
            "NO_REFUSAL: the records and the mapping disagree"
        )
    return mapping.code_for(finding.context).value


def disagreement(
    subject: str,
    run: GeneratorRun,
    screen: ScreenAnswer,
    rules: RuleRecords = PACKAGED_RULES,
) -> Disagreement | None:
    """The disagreement between one subject's generator run and screen answer, if any."""
    refused = [f for f in screen.findings if f.outcome is Outcome.REFUSED]
    reasons = tuple(sorted({_reason(f, rules) for f in refused}))
    if run.outcome is GeneratorOutcome.GENERATED:
        if not refused:
            return None
        kind = DisagreementKind.SCREEN_REFUSES_GENERATOR_BUILDS
    elif not refused:
        kind = DisagreementKind.GENERATOR_REFUSES_SCREEN_SILENT
    elif {mapped_code(f, rules) for f in refused} & set(run.codes):
        return None
    else:
        kind = DisagreementKind.CODE_UNMAPPED
    return Disagreement(subject, kind, run.codes, reasons)


# ---- the disagreement record (design D3) -------------------------------------------------------


def _entry(value: Any, where: str) -> DisagreementEntry:
    data = _fields(
        value,
        where,
        required=frozenset(
            {
                "subject",
                "kind",
                "generator_codes",
                "screen_reasons",
                "resolution",
                "r3_row",
                "owner",
                "reason",
            }
        ),
        optional=frozenset({"rg1"}),
    )
    subject = _text(data["subject"], f"{where}.subject")
    if not subject.startswith(("case:", "fixture:")):
        raise CaseAnswerError(f"{where}.subject: expected case:<id> or fixture:<path>")
    resolution = _member(Resolution, data["resolution"], f"{where}.resolution")
    rg1 = None if data.get("rg1") is None else _rg1(data["rg1"], f"{where}.rg1")
    if (resolution is Resolution.RG1_PENDING) != (rg1 is not None):
        raise CaseAnswerError(f"{where}: an rg1_pending entry names its RG1-<n>, and only one does")
    r3_row = data["r3_row"]
    return DisagreementEntry(
        disagreement=Disagreement(
            subject=subject,
            kind=_member(DisagreementKind, data["kind"], f"{where}.kind"),
            generator_codes=_sorted_texts(data["generator_codes"], f"{where}.generator_codes"),
            screen_reasons=_sorted_texts(data["screen_reasons"], f"{where}.screen_reasons"),
        ),
        resolution=resolution,
        r3_row=None if r3_row is None else _text(r3_row, f"{where}.r3_row"),
        owner=_text(data["owner"], f"{where}.owner"),
        reason=_text(data["reason"], f"{where}.reason"),
        rg1=rg1,
    )


RECORD_SCHEMA = "subset-disagreements/2"


def _record_document(path: Path) -> Mapping[str, Any]:
    where = str(path)
    data = _fields(
        json.loads(path.read_text(encoding="utf-8")),
        where,
        required=frozenset({"schema", "resolutions_decided_by", "entries"}),
    )
    if data["schema"] != RECORD_SCHEMA:
        raise CaseAnswerError(f"{where}.schema: unknown schema {data['schema']!r}")
    _member(Decider, data["resolutions_decided_by"], f"{where}.resolutions_decided_by")
    return data


def resolutions_decided_by(path: Path = DISAGREEMENTS_PATH) -> Decider:
    """Who assigned the record's resolutions, as the record states it."""
    return Decider(_record_document(path)["resolutions_decided_by"])


def read_disagreements(path: Path = DISAGREEMENTS_PATH) -> tuple[DisagreementEntry, ...]:
    """Read the hand-edited disagreement record. Nothing writes it."""
    where = str(path)
    data = _record_document(path)
    entries = tuple(
        _entry(item, f"{where}.entries[{i}]")
        for i, item in enumerate(_list(data["entries"], f"{where}.entries"))
    )
    subjects = [e.disagreement.subject for e in entries]
    if len(subjects) != len(set(subjects)):
        raise CaseAnswerError(f"{where}: a subject is listed twice")
    return entries


def recorded(found: Disagreement, entries: tuple[DisagreementEntry, ...]) -> bool:
    """Whether the record lists exactly this disagreement."""
    return any(e.disagreement == found for e in entries)
