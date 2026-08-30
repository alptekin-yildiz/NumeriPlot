"""
Dil yönetimi modülü.
Kullanım:
    from lang import set_language, t
    set_language("tr")
    print(t("app_title"))
"""

from lang import tr as _tr_mod
from lang import en as _en_mod

_LANGS = {
    "tr": _tr_mod.STRINGS,
    "en": _en_mod.STRINGS,
}

_current: dict = _tr_mod.STRINGS


def set_language(code: str) -> None:
    global _current
    _current = _LANGS.get(code, _tr_mod.STRINGS)


def get_language() -> str:
    for code, strings in _LANGS.items():
        if strings is _current:
            return code
    return "tr"


def t(key: str, **kwargs) -> str:
    """Anahtara karşılık gelen çeviriyi döndürür."""
    val = _current.get(key, key)
    if kwargs:
        try:
            return val.format(**kwargs)
        except (KeyError, ValueError):
            return val
    return val
