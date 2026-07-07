"""Unit tests for qualified name sanitization (Bug 6)."""

import pytest

from sysml_codegen.core.qualified_names import sanitize_name


class TestSanitizeNameSpecialChars:
    """Bug 6: Special character sanitization."""

    @pytest.mark.parametrize(
        "input_name, expected",
        [
            ("Racking_&_Mounting", "Racking_Mounting"),
            ("foo$bar", "foo_bar"),
            ("hello-world", "hello_world"),
            ("a@b#c", "a_b_c"),
            ("  normal  ", "normal"),
            ("'Quoted Name'", "Quoted_Name"),
            ("class", "class_"),  # reserved word still works
            ("", "unnamed"),  # SC-4 A2: empty yields a legal identifier, not ""
            (None, "unnamed"),  # SC-4 A2: None yields a legal identifier, not ""
            ("simple", "simple"),  # plain name unchanged
            ("already_valid_123", "already_valid_123"),  # underscores + digits OK
            ("___leading___", "leading"),  # leading/trailing underscores stripped
            ("$$$", "unnamed"),  # all-special produces fallback
        ],
    )
    def test_sanitize_name(self, input_name, expected):
        assert sanitize_name(input_name) == expected
