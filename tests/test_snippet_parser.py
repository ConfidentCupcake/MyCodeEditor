"""Pure-Python tests for Topic 08 placeholder parsing."""

import unittest

from code_intelligence.snippet_parser import parse_snippet


class SnippetParserTests(unittest.TestCase):
    def test_markdown_link_renders_and_tracks_ranges(self):
        result = parse_snippet("[${1:label}](${2:url})")
        self.assertEqual(result.text, "[label](url)")
        self.assertEqual(
            [(p.number, p.start, p.end) for p in result.placeholders],
            [(1, 1, 6), (2, 8, 11)],
        )

    def test_fields_follow_numeric_order_not_source_order(self):
        result = parse_snippet("${2:later} ${1:first} ${0:}")
        self.assertEqual(result.text, "later first ")
        self.assertEqual([p.number for p in result.placeholders], [1, 2, 0])

    def test_literal_text_is_preserved(self):
        result = parse_snippet("plain text")
        self.assertEqual(result.text, "plain text")
        self.assertEqual(result.placeholders, ())

    def test_zero_field_is_last(self):
        result = parse_snippet("${1:name} ${0:pass}")
        self.assertEqual(result.text, "name pass")
        self.assertEqual([p.number for p in result.placeholders], [1, 0])

    def test_unicode_character_positions_before_utf8_conversion(self):
        result = parse_snippet("é ${1:😀}")
        self.assertEqual(result.text, "é 😀")
        self.assertEqual(result.placeholders[0].start, 2)
        self.assertEqual(result.placeholders[0].end, 3)


if __name__ == "__main__":
    unittest.main()