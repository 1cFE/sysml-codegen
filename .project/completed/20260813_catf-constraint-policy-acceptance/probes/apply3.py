"""THROWAWAY (Item 5 Phase 1). Apply an edits3 group to a scratch copy."""
from __future__ import annotations
import sys
from pathlib import Path
import edits3

ACTIONS = {
    "ruled_lib": edits3.write_library,
    "g3": edits3.apply_group3,
    "g4": edits3.apply_group4,
    "g4b": edits3.apply_group4b,
    "g5": edits3.apply_group5,
    "g6": edits3.apply_group6,
}

if __name__ == "__main__":
    root = Path(sys.argv[1])
    for name in sys.argv[2:]:
        ACTIONS[name](root)
        print(f"applied {name} to {root}")
