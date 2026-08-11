"""Route-neutral selective-capture name filter (D7).

Byte-identity of untouched committed baselines is only checkable if capture is
selective: a full run re-writes every snapshot/baseline, so ``git status`` can no
longer tell a deliberate change from an incidental one. ``--fixtures NAME[,NAME...]``
restricts a run to the named fixtures; this module carries the one pure decision
both scripts share so it can be unit-tested without a syside license.

The accepted-batch driver passes stable manifest IDs as the available key space.
"""

from __future__ import annotations

from collections.abc import Iterable


def select_fixtures(available: Iterable[str], requested: str | None) -> set[str]:
    """Return the set of fixture names to capture.

    ``requested`` is the raw ``--fixtures`` value (comma-separated) or ``None`` for
    a full run. ``None`` returns every available name (backward-compatible default).
    An unknown name raises ``ValueError`` naming the offenders — fail loud, never
    silently no-op a mistyped name into an empty capture.
    """
    available_set = set(available)
    if requested is None:
        return available_set
    names = {n.strip() for n in requested.split(",") if n.strip()}
    unknown = names - available_set
    if unknown:
        raise ValueError(
            f"unknown fixture name(s): {', '.join(sorted(unknown))}. "
            f"known: {', '.join(sorted(available_set))}"
        )
    return names
