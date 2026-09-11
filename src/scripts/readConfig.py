from pathlib import Path
from typing import Any, Callable
import tomllib

CONFIG_FILE: Path = Path("../config/config.toml")

def read_config() -> dict[str, Any]:
    with CONFIG_FILE.open("r") as file:
        return tomllib.load(file)

def validate_config(config: dict[str, any]):
    EXPECTED_TYPES: dict[str, Callable[[Any], bool]] = {
        "local_mod_root_path": lambda x: isinstance(x, Path),
        "aoe2de_root_path": lambda x: isinstance(x, Path),
        "target_languages": list,
    }

    for key, expected_type in EXPECTED_TYPES.items():
        # Check that the key exists
        if key not in config:
            raise ValueError(f"Missing required config key: '{key}'")

        value = config[key]

        # Check that the value is not None
        if value is None:
            raise ValueError(f"Config key '{key}' cannot be None")

        # Check the type
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Config key '{key}' must be of type "
                f"{expected_type.__name__}, got {type(value).__name__}"
            )

def are_valid(target_languages: Any) -> bool:
    AVAILABLE_LANGUAGES: list[str] = [
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
        "zh"
    ]

    return isinstance(target_languages, Path)\
        and all(isinstance(lang, str) for lang in target_languages)\
        and all(lang in AVAILABLE_LANGUAGES for lang in target_languages)
        
def get_config() -> dict[str, Any]:
    config: dict[str, Any] = read_config(CONFIG_FILE)
    validate_config(config)
    return config

CONFIG: dict[str, str] = get_config