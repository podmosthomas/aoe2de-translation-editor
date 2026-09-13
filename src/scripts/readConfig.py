from pathlib import Path
from typing import Any

import tomllib

CONFIG_FILE = Path("../config/config.toml")

AVAILABLE_LANGUAGES = [
    "br",
    "de",
    "en",
    "es",
    "fr",
    "hi",
    "it",
    "jp",
    "ko",
    "ms",
    "mx",
    "pl",
    "ru",
    "tr",
    "tw",
    "vi",
    "zh",
]


def validate_config(config: dict[str, Any]) -> None:
    expected_types: dict[str, type] = {
        "local_mod_root_path": Path,
        "aoe2de_root_path": Path,
        "target_languages": list,
    }

    for key, expected_type in expected_types.items():
        if key not in config:
            raise ValueError(
                f"Missing required config key: '{key}'"
            )

        value = config[key]

        if value is None:
            raise ValueError(
                f"Config key '{key}' cannot be None"
            )

        if not isinstance(value, expected_type):
            raise TypeError(
                f"Config key '{key}' must be of type "
                f"{expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    target_languages = config["target_languages"]

    if not all(isinstance(lang, str) for lang in target_languages):
        raise TypeError(
            "Config key 'target_languages' must contain only strings"
        )

    if not all(lang in AVAILABLE_LANGUAGES for lang in target_languages):
        raise ValueError(
            "Config key 'target_languages' contains an "
            "unsupported language"
        )


def get_config() -> dict[str, Any]:
    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(
            f"Config file at {CONFIG_FILE} not found"
        )

    # tomllib.load() requires binary mode.
    with CONFIG_FILE.open("rb") as file:
        config: dict[str, Any] = tomllib.load(file)

    # Convert TOML path strings into Path objects.
    config["local_mod_root_path"] = Path(
        config["local_mod_root_path"]
    )
    config["aoe2de_root_path"] = Path(
        config["aoe2de_root_path"]
    )

    validate_config(config)

    return config


CONFIG = get_config()