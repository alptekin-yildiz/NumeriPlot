"""
color_themes.py — NumeriPlot renk tema tanımları.
OriginPro tema renkleri referans alınarak hazırlanmıştır.
"""
from itertools import cycle

COLOR_THEMES = {
    "Classic": [
        '#000000', '#FF0000', '#00C000', '#0000FF', '#FF00FF', 
        '#00FFFF', '#FFFF00', '#000080', '#800000', '#008080', 
        '#FF8000', '#FF0080', '#808080', '#C0C0C0', '#804000', '#008000',
    ],
    "Color4Line": [
        '#404040', '#C82323', '#2255CC', '#228833', '#9944CC', '#CC7711', '#11AAAA', '#884422', '#4477BB', '#77AA22',
        '#CC2277', '#22BB88',
    ],
    "Color4Bar": [
        '#F5C9A0', '#A8D8B0', '#C5B0D8', '#F5F0A0', '#B8C8E8',
        '#E8B0C8', '#D8C8A0', '#A8D8D8', '#E8C8B0', '#B0D0A8',
        '#D0B8D8', '#A8EEF5',
    ],
    "Candy": [
        '#EE1111', '#1144EE', '#EE8811', '#11AA33', '#BB44AA',
        '#EE5544', '#EE9911', '#11AAAA', '#AA7744', '#CC3333',
        '#44AA66', '#EE8833',
    ],
    "Bold1": [
        '#CC2222', '#2255BB', '#228833', '#882299', '#EE7711',
        '#DDDD11', '#AA5522', '#EE66AA', '#777777',
    ],
    "Bold2": [
        '#229966', '#CC6611', '#7755BB', '#DD1177', '#558822',
        '#CC8811', '#996633', '#555555',
    ],
    "Moderate2": [
        '#99BBDD', '#3366BB', '#99DDAA', '#DD9999', '#CC3333',
        '#EEAA55', '#7744AA', '#EEEE55', '#AA7733',
    ],
    "Paired Color": [
        '#AACCEE', '#2277CC', '#AADDAA', '#33AA44', '#FFAAAA',
        '#CC3333', '#FFCC88', '#EE8811', '#CCBBDD', '#7744AA',
    ],
    "Rainbow7": [
        '#EE1111', '#EE7711', '#EEEE11', '#11CC11',
        '#1111EE', '#7711EE', '#EE11CC',
    ],
}

# Scatter ve Scatter+Line için sembol döngüsü
MARKER_SEQUENCE = ['o', 's', '^', 'D', 'v', 'p', '<', 'h', '>', '*']

_current_theme_name = "Classic"

def reset_color_cycle(theme_name: str = None):
    """COLOR_CYCLE'ı seçili temadan sıfırdan başlatır."""
    global _current_theme_name
    if theme_name:
        _current_theme_name = theme_name
    return cycle(COLOR_THEMES.get(_current_theme_name, COLOR_THEMES["Classic"]))
