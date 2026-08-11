"""Exact staged source admission shared by live, capture, and freshness routes.

Admission binds a caller's model roots to one immutable set of documents before
SysIDE is allowed to see any of them. Every admitted file is copied into a
private read-only stage and parsed from there, so a source that changes mid-run
cannot silently become part of the parsed model, and the graph that comes back
can be labelled with portable ``root-N/<relpath>`` referents instead of paths
belonging to whoever happened to run the capture.

The manifest a snapshot seals — every referent with its size and SHA-256, plus
the pinned SysIDE standard library — is produced here, so ``admit_sources`` is
the one place that decides what "these sources" means.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, unquote_to_bytes, urlparse

from agentic_mbse.sysml.syside_adapter import get_syside

from sysml_codegen.core.errors import SysMLParsingError

__all__ = [
    "PINNED_STANDARD_LIBRARY_COUNT",
    "PINNED_STANDARD_LIBRARY_SHA256",
    "PINNED_SYSIDE_VERSION",
    "SourceAdmission",
    "SourceAdmissionCode",
    "SourceAdmissionError",
    "SourceFile",
    "SourceRoot",
    "StandardLibraryDigest",
    "SysideStandardLibraryDigestAdapter",
    "admit_sources",
    "validate_source_referent",
]

#: The SysIDE release this repository's admission and snapshot authority is
#: written against. The standard-library digest below is only meaningful next to
#: it, so both move together or neither does.
PINNED_SYSIDE_VERSION = "0.8.4"
PINNED_STANDARD_LIBRARY_COUNT = 94
PINNED_STANDARD_LIBRARY_SHA256 = "ada7a0818f72e95f3953e46592bec91026bbd954efda251decc35d4036272f67"
_SOURCE_SUFFIXES = frozenset({".sysml", ".kerml"})
_CANONICAL_REFERENT = re.compile(r"root-(0|[1-9][0-9]*)/(.+)")


class SourceAdmissionCode(StrEnum):
    """Closed live/capture source-admission failure vocabulary."""

    SOURCE_ROOT_INVALID = "SOURCE_ROOT_INVALID"
    SOURCE_ALIAS_COLLISION = "SOURCE_ALIAS_COLLISION"
    SOURCE_SYMLINK_ESCAPE = "SOURCE_SYMLINK_ESCAPE"
    SOURCE_READ_ERROR = "SOURCE_READ_ERROR"
    SOURCE_RACE = "SOURCE_RACE"
    SOURCE_STAGE_MUTATED = "SOURCE_STAGE_MUTATED"
    SOURCE_ADMISSION_MISMATCH = "SOURCE_ADMISSION_MISMATCH"
    SOURCE_STANDARD_LIBRARY_UNAVAILABLE = "SOURCE_STANDARD_LIBRARY_UNAVAILABLE"


class SourceAdmissionError(SysMLParsingError):
    """A model root could not be bound to one immutable staged document set."""

    def __init__(self, code: SourceAdmissionCode, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code.value}: {detail}")


@dataclass(frozen=True, slots=True)
class StandardLibraryDigest:
    kind: str
    document_count: int
    sha256: str

    def envelope_data(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "document_count": self.document_count,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class SourceRoot:
    ordinal: int
    kind: str
    display_path: Path = field(repr=False, compare=False)
    resolved_path: Path = field(repr=False, compare=False)

    def envelope_data(self) -> dict[str, object]:
        return {"ordinal": self.ordinal, "kind": self.kind}


@dataclass(frozen=True, slots=True)
class SourceFile:
    referent: str
    size_bytes: int
    sha256: str
    display_path: Path = field(repr=False, compare=False)
    resolved_path: Path = field(repr=False, compare=False)
    staged_path: Path = field(repr=False, compare=False)
    device: int = field(repr=False, compare=False)
    inode: int = field(repr=False, compare=False)
    mtime_ns: int = field(repr=False, compare=False)
    ctime_ns: int = field(repr=False, compare=False)

    def envelope_data(self) -> dict[str, object]:
        return {
            "referent": self.referent,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class SourceAdmission:
    """Immutable manifest plus the private staged files that SysIDE must parse."""

    roots: tuple[SourceRoot, ...]
    files: tuple[SourceFile, ...]
    standard_library: StandardLibraryDigest
    _stage_directory: Path = field(repr=False, compare=False)

    @property
    def staged_files(self) -> tuple[Path, ...]:
        return tuple(item.staged_path for item in self.files)

    @property
    def staged_to_referent(self) -> dict[str, str]:
        return {str(item.staged_path.resolve()): item.referent for item in self.files}

    def envelope_sources(self) -> dict[str, object]:
        """Return the sealed source manifest: ordered roots, files, fingerprint."""
        roots = [item.envelope_data() for item in self.roots]
        files = [item.envelope_data() for item in self.files]
        return {
            "roots": roots,
            "files": files,
            "fingerprint": hashlib.sha256(_canonical({"roots": roots, "files": files})).hexdigest(),
        }

    def verify_after_parse(self, model: Any) -> None:
        """Refuse source, stage, or SysIDE document-set drift after parsing."""
        syside = get_syside()
        self._verify_staged_files()
        try:
            actual = tuple(
                str(Path(uri).resolve()) for uri in model.uris(syside.DocumentKind.MODEL)
            )
        except Exception as error:
            raise SourceAdmissionError(
                SourceAdmissionCode.SOURCE_ADMISSION_MISMATCH,
                f"cannot read SysIDE model document URIs: {error}",
            ) from error
        expected = tuple(str(path.resolve()) for path in self.staged_files)
        if actual != expected or len(set(actual)) != len(actual):
            raise SourceAdmissionError(
                SourceAdmissionCode.SOURCE_ADMISSION_MISMATCH,
                f"SysIDE user documents {actual!r} do not equal admitted files {expected!r}",
            )

        self._verify_original_membership("during parse")

    def _verify_staged_files(self) -> None:
        for item in self.files:
            try:
                staged_bytes = item.staged_path.read_bytes()
            except OSError as error:
                raise SourceAdmissionError(
                    SourceAdmissionCode.SOURCE_STAGE_MUTATED,
                    f"cannot reread staged source {item.referent}: {error}",
                ) from error
            if (
                len(staged_bytes) != item.size_bytes
                or hashlib.sha256(staged_bytes).hexdigest() != item.sha256
            ):
                raise SourceAdmissionError(
                    SourceAdmissionCode.SOURCE_STAGE_MUTATED,
                    f"staged source changed during parse: {item.referent}",
                )

    def _verify_original_membership(self, interval: str) -> None:
        rescanned = _owned_files(self.roots)
        expected_membership = _admitted_membership(self.files)
        actual_membership = _scanned_membership(rescanned)
        if actual_membership != expected_membership:
            raise SourceAdmissionError(
                SourceAdmissionCode.SOURCE_RACE,
                f"source membership, ownership, identity, or metadata changed {interval}",
            )

    def close(self) -> None:
        shutil.rmtree(self._stage_directory, ignore_errors=True)

    def __enter__(self) -> SourceAdmission:
        return self

    def __exit__(
        self,
        _type: type[BaseException] | None,
        _value: BaseException | None,
        _traceback: object,
    ) -> None:
        self.close()


class SysideStandardLibraryDigestAdapter:
    """Read and fingerprint the pinned SysIDE default environment."""

    @staticmethod
    def read() -> StandardLibraryDigest:
        try:
            syside = get_syside()
            if syside.__version__ != PINNED_SYSIDE_VERSION:
                raise ValueError(
                    f"expected SysIDE {PINNED_SYSIDE_VERSION}, found {syside.__version__}"
                )
            rows: list[tuple[str, str, str]] = []
            environment = syside.Environment.get_default()
            for mutex in environment.documents:
                with mutex.lock() as document:
                    portable_name = _portable_library_name(str(document.url))
                    language = str(document.language)
                    if document.text_document is None:
                        raise ValueError(
                            f"standard-library document {portable_name} has no text document"
                        )
                    with document.text_document.lock() as text_document:
                        text = text_document.text
                    if not isinstance(text, str):
                        raise TypeError(f"standard-library text for {portable_name} is not text")
                    rows.append((portable_name, language, text))
            rows.sort()
            digest = hashlib.sha256(_canonical(rows)).hexdigest()
            result = StandardLibraryDigest("syside-default", len(rows), digest)
            if (
                result.document_count != PINNED_STANDARD_LIBRARY_COUNT
                or result.sha256 != PINNED_STANDARD_LIBRARY_SHA256
            ):
                raise ValueError(
                    "SysIDE 0.8.4 standard-library authority changed: "
                    f"count={result.document_count}, sha256={result.sha256}"
                )
            return result
        except SourceAdmissionError:
            raise
        except Exception as error:
            raise SourceAdmissionError(
                SourceAdmissionCode.SOURCE_STANDARD_LIBRARY_UNAVAILABLE,
                f"cannot read the SysIDE default standard library: {error}",
            ) from error


def admit_sources(model_paths: Sequence[Path]) -> SourceAdmission:
    """Bind ordered roots to exact staged bytes before SysIDE sees a document."""
    roots = _resolve_roots(model_paths)
    owned = _owned_files(roots)
    if not owned:
        raise SourceAdmissionError(
            SourceAdmissionCode.SOURCE_ROOT_INVALID,
            "source roots admit no lower-case .sysml or .kerml files",
        )

    stage_directory = Path(tempfile.mkdtemp(prefix="sysml-codegen-sources-"))
    try:
        stage_directory.chmod(0o700)
        files: list[SourceFile] = []
        for referent, display_path, resolved_path, scanned_stat in owned:
            source_bytes, before = _read_stable_file(resolved_path)
            if _identity(before) != _identity(scanned_stat):
                raise SourceAdmissionError(
                    SourceAdmissionCode.SOURCE_RACE,
                    f"source changed between enumeration and read: {display_path}",
                )
            try:
                source_bytes.decode("utf-8")
            except UnicodeDecodeError as error:
                raise SourceAdmissionError(
                    SourceAdmissionCode.SOURCE_READ_ERROR,
                    f"source is not UTF-8: {display_path}",
                ) from error
            staged_path = stage_directory / referent
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            staged_path.write_bytes(source_bytes)
            staged_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            digest = hashlib.sha256(source_bytes).hexdigest()
            if (
                staged_path.stat().st_size != len(source_bytes)
                or hashlib.sha256(staged_path.read_bytes()).hexdigest() != digest
            ):
                raise SourceAdmissionError(
                    SourceAdmissionCode.SOURCE_STAGE_MUTATED,
                    f"staged copy does not match admitted bytes: {referent}",
                )
            files.append(
                SourceFile(
                    referent=referent,
                    size_bytes=len(source_bytes),
                    sha256=digest,
                    display_path=display_path,
                    resolved_path=resolved_path,
                    staged_path=staged_path,
                    device=before.st_dev,
                    inode=before.st_ino,
                    mtime_ns=before.st_mtime_ns,
                    ctime_ns=before.st_ctime_ns,
                )
            )
        admission = SourceAdmission(
            roots=roots,
            files=tuple(files),
            standard_library=SysideStandardLibraryDigestAdapter.read(),
            _stage_directory=stage_directory,
        )
        admission._verify_original_membership("during admission")
        return admission
    except Exception:
        shutil.rmtree(stage_directory, ignore_errors=True)
        raise


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()


def _portable_library_name(url: str) -> str:
    path = unquote(urlparse(url).path).replace("\\", "/")
    marker = "/sysml.library/"
    if marker not in path:
        raise ValueError(f"standard-library URL has no sysml.library segment: {url}")
    name = path.split(marker, 1)[1]
    if not name:
        raise ValueError(f"standard-library URL has no portable name: {url}")
    return name


def _resolve_roots(model_paths: Sequence[Path]) -> tuple[SourceRoot, ...]:
    if isinstance(model_paths, (str, bytes)) or not isinstance(model_paths, Sequence):
        raise TypeError("model_paths must be a nonempty sequence of pathlib.Path values")
    if not model_paths:
        raise SourceAdmissionError(
            SourceAdmissionCode.SOURCE_ROOT_INVALID, "at least one source root is required"
        )
    roots: list[SourceRoot] = []
    for ordinal, supplied in enumerate(model_paths):
        if not isinstance(supplied, Path):
            raise TypeError("every model_paths member must be pathlib.Path")
        display = supplied.absolute()
        try:
            resolved = supplied.resolve(strict=True)
        except OSError as error:
            raise SourceAdmissionError(
                SourceAdmissionCode.SOURCE_ROOT_INVALID,
                f"source root does not exist: {display}",
            ) from error
        if resolved.is_file():
            if resolved.suffix not in _SOURCE_SUFFIXES:
                raise SourceAdmissionError(
                    SourceAdmissionCode.SOURCE_ROOT_INVALID,
                    f"file root must end in lower-case .sysml or .kerml: {display}",
                )
            kind = "file"
        elif resolved.is_dir():
            kind = "directory"
        else:
            raise SourceAdmissionError(
                SourceAdmissionCode.SOURCE_ROOT_INVALID,
                f"source root is not a regular file or directory: {display}",
            )
        roots.append(SourceRoot(ordinal, kind, display, resolved))
    return tuple(roots)


def _owned_files(
    roots: tuple[SourceRoot, ...],
) -> list[tuple[str, Path, Path, os.stat_result]]:
    candidates: dict[tuple[int, int], list[tuple[SourceRoot, Path, Path, os.stat_result]]] = {}
    for root in roots:
        if root.kind == "file":
            file_stat = root.resolved_path.stat()
            candidates.setdefault((file_stat.st_dev, file_stat.st_ino), []).append(
                (root, root.display_path, root.resolved_path, file_stat)
            )
            continue
        for directory, names, filenames in os.walk(root.resolved_path, followlinks=False):
            names[:] = sorted(name for name in names if not (Path(directory) / name).is_symlink())
            for filename in sorted(filenames):
                lexical = Path(directory) / filename
                if lexical.is_symlink():
                    raise SourceAdmissionError(
                        SourceAdmissionCode.SOURCE_SYMLINK_ESCAPE,
                        f"descendant file symlink is not admitted: {lexical}",
                    )
                if lexical.suffix not in _SOURCE_SUFFIXES:
                    continue
                try:
                    resolved = lexical.resolve(strict=True)
                    if not resolved.is_relative_to(root.resolved_path):
                        raise SourceAdmissionError(
                            SourceAdmissionCode.SOURCE_SYMLINK_ESCAPE,
                            f"source escapes its resolved root: {lexical}",
                        )
                    file_stat = resolved.stat()
                except SourceAdmissionError:
                    raise
                except OSError as error:
                    raise SourceAdmissionError(
                        SourceAdmissionCode.SOURCE_READ_ERROR,
                        f"cannot stat source {lexical}: {error}",
                    ) from error
                display = root.display_path / lexical.relative_to(root.resolved_path)
                candidates.setdefault((file_stat.st_dev, file_stat.st_ino), []).append(
                    (root, display, resolved, file_stat)
                )

    owned: list[tuple[str, Path, Path, os.stat_result]] = []
    collision_keys: dict[str, str] = {}
    for rows in candidates.values():
        owner, display, resolved, file_stat = min(
            rows,
            key=lambda row: (
                0 if row[0].kind == "file" else 1,
                -len(row[0].resolved_path.parts) if row[0].kind == "directory" else 0,
                row[0].ordinal,
            ),
        )
        relative = (
            resolved.name
            if owner.kind == "file"
            else str(resolved.relative_to(owner.resolved_path)).replace(os.sep, "/")
        )
        normalized = "/".join(unicodedata.normalize("NFC", part) for part in relative.split("/"))
        encoded = "/".join(_percent_encode_segment(part) for part in normalized.split("/"))
        referent = f"root-{owner.ordinal}/{encoded}"
        collision_key = os.path.normcase(referent)
        prior = collision_keys.get(collision_key)
        if prior is not None and prior != referent:
            raise SourceAdmissionError(
                SourceAdmissionCode.SOURCE_ALIAS_COLLISION,
                f"source referents collide after normalization: {prior!r}, {referent!r}",
            )
        collision_keys[collision_key] = referent
        owned.append((referent, display, resolved, file_stat))
    owned.sort(key=lambda item: item[0])
    if len({item[0] for item in owned}) != len(owned):
        raise SourceAdmissionError(
            SourceAdmissionCode.SOURCE_ALIAS_COLLISION,
            "multiple physical sources map to one logical referent",
        )
    return owned


def _percent_encode_segment(segment: str) -> str:
    result: list[str] = []
    for byte in segment.encode("utf-8"):
        character = chr(byte)
        if character.isascii() and (character.isalnum() or character in "-._~"):
            result.append(character)
        else:
            result.append(f"%{byte:02X}")
    return "".join(result)


def validate_source_referent(stored_file: str) -> str:
    """Validate and return one canonical v6 logical source referent."""
    match = _CANONICAL_REFERENT.fullmatch(stored_file)
    if match is None:
        raise ValueError(f"invalid canonical source referent: {stored_file!r}")
    payload = match.group(2)
    segments = payload.split("/")
    if not segments or not payload.endswith((".sysml", ".kerml")):
        raise ValueError(f"invalid canonical source referent: {stored_file!r}")
    for encoded in segments:
        if not encoded:
            raise ValueError(f"invalid canonical source referent: {stored_file!r}")
        try:
            decoded = unquote_to_bytes(encoded).decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"invalid canonical source referent: {stored_file!r}") from error
        if decoded in ("", ".", "..") or "/" in decoded or "\\" in decoded:
            raise ValueError(f"invalid canonical source referent: {stored_file!r}")
        if quote(decoded, safe="-._~", encoding="utf-8") != encoded:
            raise ValueError(f"invalid canonical source referent: {stored_file!r}")
    return stored_file


def _read_stable_file(path: Path) -> tuple[bytes, os.stat_result]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            before = os.fstat(descriptor)
            chunks: list[bytes] = []
            while chunk := os.read(descriptor, 1024 * 1024):
                chunks.append(chunk)
            after = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        raise SourceAdmissionError(
            SourceAdmissionCode.SOURCE_READ_ERROR, f"cannot read source {path}: {error}"
        ) from error
    if _identity(before) != _identity(after):
        raise SourceAdmissionError(
            SourceAdmissionCode.SOURCE_RACE, f"source changed while being read: {path}"
        )
    return b"".join(chunks), before


def _identity(file_stat: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        file_stat.st_dev,
        file_stat.st_ino,
        file_stat.st_size,
        file_stat.st_mtime_ns,
        file_stat.st_ctime_ns,
    )


def _admitted_membership(
    files: tuple[SourceFile, ...],
) -> list[tuple[str, int, int, int, int, int]]:
    return [
        (
            item.referent,
            item.device,
            item.inode,
            item.size_bytes,
            item.mtime_ns,
            item.ctime_ns,
        )
        for item in files
    ]


def _scanned_membership(
    scanned: list[tuple[str, Path, Path, os.stat_result]],
) -> list[tuple[str, int, int, int, int, int]]:
    return [
        (
            referent,
            file_stat.st_dev,
            file_stat.st_ino,
            file_stat.st_size,
            file_stat.st_mtime_ns,
            file_stat.st_ctime_ns,
        )
        for referent, _display, _path, file_stat in scanned
    ]
