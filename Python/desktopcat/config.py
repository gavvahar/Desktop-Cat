"""Local JSON config file (see plan's "Config & data" section). No network,
no accounts -- just ~/.config/desktopcat/config.json. Plain functions, no
classes.
"""

import json, os

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "desktopcat")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "name": "",
    "fur_color": None,  # [r, g, b] or None for the default palette
    "reminders": {
        "stretch": {"enabled": True, "interval_minutes": 30},
        "water": {"enabled": True, "interval_minutes": 45},
        "custom": [],  # list of {"interval_minutes": int, "text": str}
        "pinned_message": "",
    },
    "pomodoro": {"enabled": False, "focus_minutes": 25, "break_minutes": 5},
}


def load_config():
    if not os.path.isfile(CONFIG_PATH):
        return _deep_copy(DEFAULTS)
    try:
        with open(CONFIG_PATH) as fh:
            user_config = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return _deep_copy(DEFAULTS)
    return _merge_defaults(DEFAULTS, user_config)


def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as fh:
        json.dump(config, fh, indent=2)


def _deep_copy(value):
    return json.loads(json.dumps(value))


def _merge_defaults(defaults, override):
    result = _deep_copy(defaults)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_defaults(result[key], value)
        else:
            result[key] = value
    return result
