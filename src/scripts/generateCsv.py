from __future__ import annotations

import csv
from pathlib import Path

import readConfig


TRANSLATION_KEY_VALUE_SEPARATOR = " "
COMMENT_MARKER = "//"

ORIGINAL_LANGUAGE = "en"

AOE2DE_ROOT_PATH_KEY = "aoe2de_root_path"
TARGET_LANGUAGES_KEY = "target_languages"

OUTPUT_DIRECTORY = Path("../../csv")


def read_translations(path: Path) -> dict[str, str]:
    """
    Read an AoE2 key-value string file.

    The first space separates the ID from the value.
    Everything starting at the first '//' is treated as a comment.
    """

    strings: dict[str, str] = {}

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            # Remove newline characters only.
            line = line.rstrip("\r\n")

            # Skip empty lines and lines starting with //.
            if not line.strip() or line.lstrip().startswith(COMMENT_MARKER):
                continue

            # Remove inline comments.
            comment_position = line.find(COMMENT_MARKER)
            if comment_position != -1:
                line = line[:comment_position]

            # The first space is the key/value separator.
            separator_position = line.find(TRANSLATION_KEY_VALUE_SEPARATOR)

            if separator_position == -1:
                continue

            key = line[:separator_position].strip()
            value = line[separator_position + 1:].strip()

            # Require both an ID and a value.
            if not key or not value:
                continue

            strings[key] = value

    return strings


def sort_key(item: tuple[str, dict]) -> tuple[int, int | str]:
    """Sort numeric IDs numerically and anything else alphabetically."""

    key = item[0]

    try:
        return (0, int(key))
    except ValueError:
        return (1, key)


def get_key_value_strings_path(root_path: Path, lang: str) -> Path:
    return (
        root_path
        / "resources"
        / lang
        / "strings"
        / "key-value"
        / "key-value-strings-utf8.txt"
    )


def get_output_file_path(lang: str) -> Path:
    return OUTPUT_DIRECTORY / f"translations-{lang}.csv"


def create_rows(
    original: dict[str, str],
    translation: dict[str, str],
) -> list[dict[str, str]]:
    """
    Create the merged CSV rows.

    This is an outer JOIN on the string ID.
    """

    all_ids = set(original) | set(translation)

    rows = []

    for string_id in all_ids:
        rows.append(
            {
                "id": string_id,
                "english": original.get(string_id, ""),
                "translation": translation.get(string_id, ""),
                "note": "",
            }
        )

    rows.sort(key=lambda row: sort_key((row["id"], row)))

    return rows


def write_csv(
    output_file: Path,
    rows: list[dict[str, str]],
    translation_language: str,
) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "english",
                "translation",
                "note",
            ],
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "id": row["id"],
                    "english": row["english"],
                    translation_language: row["translation"],
                    "note": row["note"],
                }
            )


def main() -> None:
    aoe2de_root_path: Path = readConfig.CONFIG[AOE2DE_ROOT_PATH_KEY]
    target_languages: list[str] = readConfig.CONFIG[TARGET_LANGUAGES_KEY]

    original_file = get_key_value_strings_path(
        aoe2de_root_path,
        ORIGINAL_LANGUAGE,
    )

    if not original_file.is_file():
        raise FileNotFoundError(
            f"English string file not found:\n{original_file}"
        )

    print(f"Reading English strings from:\n  {original_file}")
    original_strings = read_translations(original_file)

    for language in target_languages:
        translation_file = get_key_value_strings_path(
            aoe2de_root_path,
            language,
        )

        if not translation_file.is_file():
            raise FileNotFoundError(
                f"Translation string file not found:\n{translation_file}"
            )

        print(f"Reading {language} strings from:\n  {translation_file}")
        translation_strings = read_translations(translation_file)

        rows = create_rows(
            original_strings,
            translation_strings,
        )

        output_file = get_output_file_path(language)

        write_csv(
            output_file,
            rows,
            language,
        )

        print()
        print(f"English strings: {len(original_strings)}")
        print(f"{language} strings:  {len(translation_strings)}")
        print(f"Merged IDs:       {len(rows)}")
        print(f"Written to:       {output_file.resolve()}")
        print()
        

if __name__ == "__main__":
    main()
