import pytest

from src.utils.markup_parser import strip_markup, to_html


class TestMarkupParser:
    def test_strip_markup(self):
        # Basic tags
        assert strip_markup("<c(FFFFFF)>Hello</c>") == "Hello"

        # Multiple tags and no closing tags in some parts
        text = " [ =<c(B22222)>GOH ARm</c>= - Authenticity ] v4.02"
        assert strip_markup(text) == " [ =GOH ARm= - Authenticity ] v4.02"

        # Empty or no tags
        assert strip_markup("No tags here") == "No tags here"
        assert strip_markup("") == ""

    def test_to_html(self):
        # Basic conversion
        assert (
            to_html("<c(FFFFFF)>Hello</c>")
            == '<span style="color:#FFFFFF;">Hello</span>'
        )

        # Complex description from real mod.info
        text = "ID:<c(FFFFFF)>286</c> GOH\n <c(bdba09)>STEP I</c>"
        expected = 'ID:<span style="color:#FFFFFF;">286</span> GOH<br> <span style="color:#bdba09;">STEP I</span>'
        assert to_html(text) == expected

        # Literal \n vs Actual newline
        assert to_html("Line 1\\nLine 2\nLine 3") == "Line 1<br>Line 2<br>Line 3"
