import pytest

from src.analysis.text_utils import format_panel_label, get_text_preset


@pytest.mark.parametrize(
    ("idx", "style", "expected"),
    [
        (0, "lower_paren", "(a)"),
        (0, "lower_rparen", "a)"),
        (1, "lower", "b"),
        (0, "upper_paren", "(A)"),
        (0, "upper_rparen", "A)"),
        (2, "upper", "C"),
        (0, "num_paren", "(1)"),
        (0, "num_rparen", "1)"),
        (3, "num", "4"),
        (26, "lower", "aa"),
    ],
)
def test_format_panel_label(idx, style, expected):
    assert format_panel_label(idx, style) == expected


def test_get_text_preset_top_left():
    assert get_text_preset("top_left") == (0.02, 0.98, "left", "top")


def test_get_text_preset_unknown_returns_center():
    assert get_text_preset("unknown") == (0.50, 0.50, "center", "center")
