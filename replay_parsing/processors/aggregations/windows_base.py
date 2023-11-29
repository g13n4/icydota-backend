from typing import Dict

WINDOWS_BASE: Dict[str, int | None | str] = {
    'l2': None,
    'l4': None,
    'l6': None,
    'l8': None,
    'l10': None,

    # next phase
    'g15': None,
    'g30': None,
    'g45': None,
    'g60': None,
    'g60plus': None,
}

WINDOWS_BASE_NULLS: Dict[str, int] = {
    'l2': 0,
    'l4': 0,
    'l6': 0,
    'l8': 0,
    'l10': 0,

    # next phase
    'g15': 0,
    'g30': 0,
    'g45': 0,
    'g60': 0,
    'g60plus': 0,
}
