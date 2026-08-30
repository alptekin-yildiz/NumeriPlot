from __future__ import annotations


def _index_to_letters(index: int, uppercase: bool = False) -> str:
    """0 -> a, 25 -> z, 26 -> aa, ..."""
    if index < 0:
        raise ValueError("index must be >= 0")
    base = ord("A" if uppercase else "a")
    n = index
    out = []
    while True:
        n, rem = divmod(n, 26)
        out.append(chr(base + rem))
        if n == 0:
            break
        n -= 1
    return "".join(reversed(out))


def format_panel_label(index: int, style: str) -> str:
    """
    style:
      - lower_paren: (a), (b), ...
      - lower_rparen: a), b), ...
      - lower: a, b, ...
      - upper_paren: (A), (B), ...
      - upper_rparen: A), B), ...
      - upper: A, B, ...
      - num_paren: (1), (2), ...
      - num_rparen: 1), 2), ...
      - num: 1, 2, ...
    """
    if style == "num_paren":
        return f"({index + 1})"
    if style == "num_rparen":
        return f"{index + 1})"
    if style == "num":
        return str(index + 1)
    if style == "upper_paren":
        return f"({_index_to_letters(index, uppercase=True)})"
    if style == "upper_rparen":
        return f"{_index_to_letters(index, uppercase=True)})"
    if style == "upper":
        return _index_to_letters(index, uppercase=True)
    if style == "lower":
        return _index_to_letters(index, uppercase=False)
    if style == "lower_rparen":
        return f"{_index_to_letters(index, uppercase=False)})"
    # default: lower_paren
    return f"({_index_to_letters(index, uppercase=False)})"


def get_text_preset(preset: str) -> tuple[float, float, str, str]:
    """
    Returns (x, y, ha, va) for axes coordinates.
    """
    presets = {
        "top_left": (0.02, 0.98, "left", "top"),
        "top_center": (0.50, 0.98, "center", "top"),
        "top_right": (0.98, 0.98, "right", "top"),
        "center_left": (0.02, 0.50, "left", "center"),
        "center": (0.50, 0.50, "center", "center"),
        "center_right": (0.98, 0.50, "right", "center"),
        "bottom_left": (0.02, 0.02, "left", "bottom"),
        "bottom_center": (0.50, 0.02, "center", "bottom"),
        "bottom_right": (0.98, 0.02, "right", "bottom"),
    }
    return presets.get(preset, (0.50, 0.50, "center", "center"))
