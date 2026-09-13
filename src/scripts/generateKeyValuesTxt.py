from __future__ import annotations

import csv
from pathlib import Path

import readConfig
import generateCsv


TRANSLATION_DIRECTORY = Path("../../csv")


def get_translation_file_path(language: str) -> Path:
    return (
        TRANSLATION_DIRECTORY
        / f"translations-{language}.csv"
    )


def get_modded_strings_path(
    local_mod_root_path: Path,
    language: str,
) -> Path:
    return (
        local_mod_root_path
        / "resources"
        / language
        / "strings"
        / "key-value"
        / "key-value-modded-strings-utf8.txt"
    )


def read_csv_translations(path: Path) -> dict[str, str]:
    translations: dict[str, str] = {}

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            string_id = row["id"]
            translation = row["translation"]

            translations[string_id] = translation

    return translations


def get_changed_translations(
    csv_translations: dict[str, str],
    game_translations: dict[str, str],
) -> dict[str, str]:
    changed_translations: dict[str, str] = {}

    for string_id, translation in csv_translations.items():
        game_translation = game_translations.get(string_id)

        if translation and translation != game_translation:
            changed_translations[string_id] = translation

    return changed_translations


def write_modded_strings(
    path: Path,
    translations: dict[str, str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="\n") as file:
        for string_id, translation in translations.items():
            file.write(f"{string_id} {translation}\n")


def main() -> None:
    local_mod_root_path: Path = readConfig.CONFIG[
        "local_mod_root_path"
    ]
    aoe2de_root_path: Path = readConfig.CONFIG[
        "aoe2de_root_path"
    ]

    for language in readConfig.AVAILABLE_LANGUAGES:
        csv_file = get_translation_file_path(language)

        if not csv_file.is_file():
            continue

        game_file = generateCsv.get_key_value_strings_path(
            aoe2de_root_path,
            language,
        )

        if not game_file.is_file():
            raise FileNotFoundError(
                f"Game translation file for '{language}' "
                f"not found: {game_file}"
            )

        print(f"Processing language: {language}")

        csv_translations = read_csv_translations(csv_file)
        game_translations = generateCsv.read_translations(game_file)

        changed_translations = get_changed_translations(
            csv_translations,
            game_translations,
        )

        output_file = get_modded_strings_path(
            local_mod_root_path,
            language,
        )

        write_modded_strings(
            output_file,
            changed_translations,
        )

        print(
            f"  CSV translations: {len(csv_translations)}"
        )
        print(
            f"  Changed translations: "
            f"{len(changed_translations)}"
        )
        print(f"  Output: {output_file}")


if __name__ == "__main__":
    main()