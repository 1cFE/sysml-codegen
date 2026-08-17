"""Exact authored metadata carried by one SysML feature declaration."""

from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = ["extract_feature_unit"]

_ISQ_UNITS = {
    "Length": "m",
    "Mass": "kg",
    "Time": "s",
    "ElectricCurrent": "A",
    "ThermodynamicTemperature": "K",
    "AmountOfSubstance": "mol",
    "LuminousIntensity": "cd",
    "Power": "W",
    "Energy": "J",
    "Force": "N",
    "Pressure": "Pa",
    "Frequency": "Hz",
    "Voltage": "V",
    "ElectricResistance": "Ω",
    "MagneticFluxDensity": "T",
    "Area": "m²",
    "Volume": "m³",
    "Velocity": "m/s",
    "Acceleration": "m/s²",
    "Density": "kg/m³",
    "HeatFlux": "W/m²",
}

_SI_UNITS = {
    "Metre": "m",
    "Kilogram": "kg",
    "Second": "s",
    "Ampere": "A",
    "Kelvin": "K",
    "Mole": "mol",
    "Candela": "cd",
    "Watt": "W",
    "Joule": "J",
    "Newton": "N",
    "Pascal": "Pa",
    "Hertz": "Hz",
    "Volt": "V",
    "Ohm": "Ω",
    "Tesla": "T",
}


def extract_feature_unit(
    feature: Any,
    *,
    model_paths: Sequence[Path] = (),
) -> str | None:
    """Return one feature's exact authored unit without inference or conversion."""
    return (
        _unit_from_type(feature)
        or _unit_from_source(feature, model_paths=model_paths)
        or _unit_from_description(_description(feature))
    )


def _unit_from_type(feature: Any) -> str | None:
    for relationship, target in getattr(feature, "heritage", ()) or ():
        if not SysideAdapter.is_instance(relationship, "FeatureTyping"):
            continue
        name = str(getattr(target, "name", None) or "")
        unit = _ISQ_UNITS.get(name)
        if unit is not None:
            return unit
        unit = _SI_UNITS.get(name)
        if unit is not None:
            return unit
    return None


def _unit_from_source(feature: Any, *, model_paths: Sequence[Path]) -> str | None:
    cst_node = getattr(feature, "cst_node", None)
    start_byte = getattr(cst_node, "start_byte", None)
    if start_byte is None:
        return None
    source_file = _source_file(feature, model_paths=model_paths)
    if source_file is None or not source_file.exists():
        return None
    try:
        source_content = source_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None

    cumulative = 0
    source_line = None
    for line in source_content.split("\n"):
        if cumulative <= start_byte < cumulative + len(line) + 1:
            source_line = line
            break
        cumulative += len(line) + 1
    if not source_line:
        return None

    match = re.search(r"//\s*(\[?[A-Za-z°Ω²³/·⋅\-]+\]?)\s*(?:-|$|\s)", source_line)
    if match is None:
        return None
    unit = match.group(1).strip("[]")
    if unit.lower() in {
        "the",
        "this",
        "that",
        "from",
        "todo",
        "note",
        "fixme",
        "energy",
        "power",
    }:
        return None
    return unit


def _source_file(feature: Any, *, model_paths: Sequence[Path]) -> Path | None:
    current = feature
    while current is not None:
        document = getattr(current, "document", None)
        url = getattr(document, "url", None)
        if url is not None:
            path = getattr(url, "path", None)
            if path is not None:
                return Path(path)
            url_text = str(url)
            return Path(url_text[5:] if url_text.startswith("file:") else url_text)
        source_file = getattr(current, "source_file", None)
        if source_file:
            return Path(source_file)
        owning_document = getattr(current, "owning_document", None)
        uri = getattr(owning_document, "uri", None)
        if uri:
            return Path(uri)
        current = getattr(current, "owner", None)

    return None


def _description(feature: Any) -> str:
    for document in getattr(feature, "documentation", ()) or ():
        body = getattr(document, "body", None)
        if body:
            return str(body).strip()
    return ""


def _unit_from_description(description: str) -> str | None:
    if not description:
        return None
    match = re.search(r"\[([A-Za-z°Ω²³/·⋅\-]+)\]", description)
    if match:
        return match.group(1)
    match = re.match(r"^([A-Za-z°Ω²³/·⋅]+)\s*[-–—]", description)
    if match:
        unit = match.group(1)
        if unit.lower() not in {"the", "this", "that", "total", "maximum", "minimum"}:
            return unit
    match = re.search(r"\(([A-Za-z°Ω²³/·⋅\-]+)\)", description)
    if match:
        unit = match.group(1)
        if len(unit) <= 10 and not unit.lower().startswith(("e.g", "i.e", "typ", "def")):
            return unit
    return None
