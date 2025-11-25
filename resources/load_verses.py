from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from build_verses import Verse


def _load_json(path: Path | str) -> list[dict[str, Any]]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _build_verses(raw: list[dict[str, Any]]) -> tuple[list[Verse], dict[str, Verse]]:
    verses: list[Verse] = []
    by_id: dict[str, Verse] = {}
    for item in raw:
        verse = Verse(
            book=int(item["book"]),
            line_numbers=tuple(int(n) for n in item["line_numbers"]), #type: ignore
            paragraphs=item["paragraphs"],
            corresponding=[],
        )
        verses.append(verse)
        by_id[item["id"]] = verse
    return verses, by_id


def _attach_corresponding(
    raw: list[dict[str, Any]], own: list[Verse], other_lookup: dict[str, Verse]
) -> None:
    for item, verse in zip(raw, own):
        for cid in item.get("correspondingIds", []):
            other = other_lookup.get(cid)
            if other is None:
                continue
            if other not in verse.corresponding:
                verse.corresponding.append(other)
            if verse not in other.corresponding:
                other.corresponding.append(verse)


def load_json_verses(
    latin_path: Path | str = "latin_verses.json",
    english_path: Path | str = "english_verses.json",
) -> tuple[list[Verse], list[Verse]]:
    latin_raw = _load_json(latin_path)
    english_raw = _load_json(english_path)

    latin_verses, latin_lookup = _build_verses(latin_raw)
    english_verses, english_lookup = _build_verses(english_raw)

    _attach_corresponding(latin_raw, latin_verses, english_lookup)
    _attach_corresponding(english_raw, english_verses, latin_lookup)

    return latin_verses, english_verses

def check_correct_correspondence(
    latin: list[Verse],
    english: list[Verse],
) -> None:
    for latin_verse in latin:
        l_start, l_end = latin_verse.line_numbers

        english_corresponding = latin_verse.corresponding
        for eng_verse in english_corresponding:
            e_start, e_end = eng_verse.line_numbers

            if l_start <= e_start or l_end >= e_end:
                pass
            elif l_start >= e_start or l_end <= e_end:
                pass
            else:
                raise ValueError(
                    f"Incorrect correspondence between Latin verse "
                    f"{latin_verse} and English verse {eng_verse}."
                )
    
    for english_verse in english:
        e_start, e_end = english_verse.line_numbers

        latin_corresponding = english_verse.corresponding
        for lat_verse in latin_corresponding:
            l_start, l_end = lat_verse.line_numbers

            if l_start <= e_start or l_end >= e_end:
                pass
            elif l_start >= e_start or l_end <= e_end:
                pass
            else:
                raise ValueError(
                    f"Incorrect correspondence between Latin verse "
                    f"{english_verse} and English verse {lat_verse}."
                )
    
    print("CORRECT")

def main():
    # TODO: Time loading function
    latin, english = load_json_verses()
    check_correct_correspondence(latin, english)

    

if __name__ == "__main__":
    main()
