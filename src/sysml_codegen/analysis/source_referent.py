"""Portable source referents for the live route.

``map_live_source_referent`` renders the same ``root-N/<relpath>`` shape the
capture route's admission manifest produces, derived from the caller's model
roots instead of a staged manifest — segments NFC-normalized, then
percent-encoded, exactly as ``extraction/source_manifest.py`` encodes them, so
the two routes cannot split on rendering.
"""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote_to_bytes

_CANONICAL_PATTERN = re.compile(r"root-(0|[1-9][0-9]*)/(.+)")
_SEGMENT_SAFE = "-._~"


def _lexical_absolute(path: str | Path) -> str:
    return os.path.abspath(os.path.normpath(os.fspath(path)))


def _is_contained(source: str, boundary: str) -> bool:
    try:
        return os.path.commonpath((source, boundary)) == boundary
    except ValueError:
        return False


def _encode_relative_path(relative_path: str) -> str:
    segments = Path(relative_path).parts
    if not segments or any(segment in ("", ".", "..") for segment in segments):
        raise ValueError(f"source path has no canonical relative segments: {relative_path!r}")
    return "/".join(
        quote(unicodedata.normalize("NFC", segment), safe=_SEGMENT_SAFE, encoding="utf-8")
        for segment in segments
    )


def map_live_source_referent(raw_file: str, model_paths: list[Path]) -> str:
    """Map one raw parser file to a portable, ordered-root-relative referent."""
    source = _lexical_absolute(raw_file)
    candidates: list[tuple[int, int, str]] = []
    missing_roots: list[str] = []
    for slot, model_path in enumerate(model_paths):
        root = _lexical_absolute(model_path)
        if os.path.isfile(root):
            if source == root:
                candidates.append((2, slot, os.path.basename(root)))
            continue
        if not os.path.isdir(root):
            missing_roots.append(root)
            continue
        if _is_contained(source, root):
            relative = os.path.relpath(source, root)
            candidates.append((1 + len(Path(root).parts), slot, relative))

    if not candidates:
        detail = f"; missing roots: {missing_roots!r}" if missing_roots else ""
        raise ValueError(f"raw source {raw_file!r} does not match any supplied model root{detail}")

    exact_file_candidates = [candidate for candidate in candidates if candidate[0] == 2]
    if exact_file_candidates:
        _, slot, relative = min(exact_file_candidates, key=lambda item: item[1])
    else:
        _, slot, relative = max(candidates, key=lambda item: (item[0], -item[1]))
    return f"root-{slot}/{_encode_relative_path(relative)}"


def validate_snapshot_source_referent(stored_file: str) -> str:
    """Validate and return one already-canonical snapshot source referent."""
    match = _CANONICAL_PATTERN.fullmatch(stored_file)
    if match is None:
        raise ValueError(f"invalid canonical source referent: {stored_file!r}")
    payload = match.group(2)
    segments = payload.split("/")
    for encoded in segments:
        if not encoded:
            raise ValueError(f"invalid canonical source referent: {stored_file!r}")
        try:
            decoded = unquote_to_bytes(encoded).decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"invalid canonical source referent: {stored_file!r}") from error
        if decoded in ("", ".", "..") or "/" in decoded or "\\" in decoded:
            raise ValueError(f"invalid canonical source referent: {stored_file!r}")
        if quote(decoded, safe=_SEGMENT_SAFE, encoding="utf-8") != encoded:
            raise ValueError(f"invalid canonical source referent: {stored_file!r}")
    return stored_file
