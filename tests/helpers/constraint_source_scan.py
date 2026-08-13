"""Read authored constraint usages straight out of `.sysml` text, license-free.

This exists so the totality claim is checked against something that does **not** descend
from the thing it checks. Every other artifact in the constraint chain — catalog, snapshot,
requirement rows — is a projection of the elaborated domain, so comparing any two of them
compares two views of the same population and would pass even if that population were
truncated. This reader shares no code, no adapter, and no parse with the elaborator: it
reads the source text the author wrote.

It is a heuristic, deliberately, and it is never the authority. Its job is to keep the
reviewed expectation files honest as fixtures change. Known failure classes, stated because
a heuristic that hides them is worse than no heuristic:

- **False negative:** a declaration split across lines between the keyword and the name.
- **False negative:** an annotation-prefixed form (`#meta constraint c { … }`).
- **False positive:** the keyword inside a string literal that survives comment stripping.
- **Approximate:** the owner qualified name is built from enclosing `package` / `… def` /
  named-usage headers, so a shape this does not model would attribute a usage to the wrong
  enclosing scope.

When the scanner and an expectation file disagree, the **expectation file** is re-derived
from source by hand. The scanner never edits it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "ConstraintDeclaration",
    "MARKER_PATTERN",
    "scan_constraint_declarations",
    "scan_inapplicable_markers",
    "strip_comments",
]

#: Statement-initial keywords that declare a constraint *usage*. `constraint def` is a
#: definition and is excluded by the negative lookahead.
_USAGE_PATTERN = re.compile(
    r"^\s*(?:(?:require|assume)\s+(?:not\s+)?constraint"
    r"|assert\s+(?:not\s+)?constraint"
    r"|satisfy(?:\s+requirement)?"
    r"|constraint(?!\s+def\b))\b"
    r"(?:\s+(?P<name>'[^']+'|[A-Za-z_][A-Za-z0-9_]*))?"
)

#: Headers that open a named scope contributing a qualified-name segment.
_SCOPE_PATTERN = re.compile(
    r"^\s*(?:(?:abstract|variation)\s+)?"
    r"(?:package|library\s+package"
    r"|(?:part|calc|constraint|requirement|attribute|item|action|state|port|analysis"
    r"|verification|use\s+case|view|concern)\s+def"
    r"|part|calc|requirement|attribute|item|action|state|port)\b"
    r"\s+(?P<name>'[^']+'|[A-Za-z_][A-Za-z0-9_]*)"
)

#: The inapplicability marker, as it appears in `.sysml` text rather than in a parsed body.
MARKER_PATTERN = re.compile(r"@inapplicable\b")


@dataclass(frozen=True)
class ConstraintDeclaration:
    """One authored constraint usage, as the source text states it."""

    usage_qualified_name: str
    owner_qualified_name: str
    source_file: str
    source_line: int

    def as_row(self) -> dict[str, object]:
        return {
            "usage_qualified_name": self.usage_qualified_name,
            "owner_qualified_name": self.owner_qualified_name,
            "source_file": self.source_file,
            "source_line": self.source_line,
        }


def strip_comments(text: str) -> str:
    """Blank out `//` line comments and `/* … */` blocks, preserving line numbering.

    Replacing rather than deleting is what keeps a reported line number equal to the line
    number in the file the reader will open.
    """
    out: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == "/" and text.startswith("//", index):
            end = text.find("\n", index)
            end = length if end == -1 else end
            out.append(" " * (end - index))
            index = end
        elif char == "/" and text.startswith("/*", index):
            end = text.find("*/", index + 2)
            end = length if end == -1 else end + 2
            out.append("".join("\n" if c == "\n" else " " for c in text[index:end]))
            index = end
        else:
            out.append(char)
            index += 1
    return "".join(out)


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _segment(name: str) -> str:
    """One qualified-name segment, spelled the way the parser reports it.

    A quoted name keeps its quotes in the qualified name only when it *needs* them:
    ``'Toy Plant'`` stays quoted, ``'Divertor'`` comes back bare because it was already a
    legal identifier. Getting this wrong would make every expectation row for a quoted
    owner disagree over punctuation rather than over population, which is exactly the kind
    of noise that trains a reader to ignore the oracle.
    """
    if name.startswith("'") and _IDENTIFIER.match(name[1:-1]):
        return name[1:-1]
    return name


def scan_constraint_declarations(directory: Path) -> list[ConstraintDeclaration]:
    """Every constraint usage declared under ``directory``, sorted by file then line."""
    found: list[ConstraintDeclaration] = []
    for path in sorted(directory.rglob("*.sysml")):
        found.extend(_scan_file(path, path.relative_to(directory).as_posix()))
    return found


def _scan_file(path: Path, referent: str) -> list[ConstraintDeclaration]:
    lines = strip_comments(path.read_text()).split("\n")
    found: list[ConstraintDeclaration] = []
    # (segment, depth-at-which-it-opened). A segment closes when depth falls back to it.
    scopes: list[tuple[str, int]] = []
    depth = 0
    for number, line in enumerate(lines, start=1):
        usage = _USAGE_PATTERN.match(line)
        scope = None if usage else _SCOPE_PATTERN.match(line)
        owner = "::".join(segment for segment, _ in scopes)
        if usage is not None:
            name = _segment(usage.group("name") or "")
            found.append(
                ConstraintDeclaration(
                    usage_qualified_name=f"{owner}::{name}" if name else "<anonymous>",
                    owner_qualified_name=owner,
                    source_file=referent,
                    source_line=number,
                )
            )
        opened = line.count("{")
        closed = line.count("}")
        if scope is not None and opened:
            scopes.append((_segment(scope.group("name")), depth))
        depth += opened - closed
        while scopes and depth <= scopes[-1][1]:
            scopes.pop()
    return found


def scan_inapplicable_markers(directory: Path) -> list[tuple[str, int]]:
    """Every ``@inapplicable`` marker in the source text, as ``(referent, line)``.

    Read from source rather than from the graph on purpose. SysIDE drops a ``doc`` comment
    written inside an inline-predicate constraint body, so a marker on that shape never
    reaches elaboration and the strict parse's near-miss halt cannot fire. Comparing what
    the author wrote against what the domain carries is what makes that gap loud instead of
    silent.
    """
    markers: list[tuple[str, int]] = []
    for path in sorted(directory.rglob("*.sysml")):
        referent = path.relative_to(directory).as_posix()
        # Read raw, not comment-stripped: the marker lives *inside* a comment body.
        for number, line in enumerate(path.read_text().split("\n"), start=1):
            if MARKER_PATTERN.search(line):
                markers.append((referent, number))
    return markers
