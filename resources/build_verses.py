from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from typing import TypeGuard
import json


@dataclass
class Verse:
    book: int
    line_numbers: tuple[int, int]
    paragraphs: list[list[str]]
    corresponding: list["Verse"]


TextToken = tuple[str, str]
MilestoneToken = tuple[str, dict]
Token = TextToken | MilestoneToken
Segment = tuple[str, str | ET.Element]


def is_line_token(token: Token) -> TypeGuard[TextToken]:
    return token[0] == "line"


def is_milestone_token(token: Token) -> TypeGuard[MilestoneToken]:
    return token[0] == "milestone"


def is_text_segment(segment: Segment) -> TypeGuard[tuple[str, str]]:
    return segment[0] == "text"


def is_milestone_segment(segment: Segment) -> TypeGuard[tuple[str, ET.Element]]:
    return segment[0] == "milestone"


def normalize_text(text: str) -> str:
    """Collapse whitespace inside a line fragment."""
    return re.sub(r"\s+", " ", text).strip()


def collect_text_segments(elem: ET.Element) -> list[str]:
    """Collect all text content inside an element, ignoring the tags themselves."""
    segments: list[str] = []
    if elem.text:
        segments.append(elem.text)
    for child in elem:
        segments.extend(collect_text_segments(child))
        if child.tail:
            segments.append(child.tail)
    return segments


def append_to_previous_line(tokens: list[Token], text: str) -> None:
    """Append text to the most recent line token if present."""
    if not text:
        return

    for idx in range(len(tokens) - 1, -1, -1):
        token = tokens[idx]
        if is_line_token(token):
            kind, value = token
            joiner = "" if value.endswith(" ") or text.startswith(" ") else " "
            tokens[idx] = (kind, f"{value}{joiner}{text}".strip())
            return
    tokens.append(("line", text))


def process_line_element(line_elem: ET.Element, tokens: list[Token]) -> None:
    """Flatten a <l> element, moving milestones out and merging stray text."""
    segments: list[Segment] = []
    if line_elem.text:
        segments.append(("text", line_elem.text))

    for child in line_elem:
        if child.tag == "milestone":
            segments.append(("milestone", child))
        else:
            for text in collect_text_segments(child):
                segments.append(("text", text))
        if child.tail:
            segments.append(("text", child.tail))

    text_buffer: list[str] = []
    for segment in segments:
        if is_text_segment(segment):
            text_buffer.append(segment[1])
            continue

        prefix = normalize_text("".join(text_buffer))
        if prefix:
            append_to_previous_line(tokens, prefix)
        text_buffer = []
        if is_milestone_segment(segment):
            milestone_elem = segment[1]
            tokens.append(("milestone", milestone_elem.attrib))

    final_text = normalize_text("".join(text_buffer))
    if final_text:
        tokens.append(("line", final_text))


def flatten_div(div_elem: ET.Element) -> list[Token]:
    """Convert a <div1> element into a linear stream of milestones and lines."""
    tokens: list[Token] = []
    for child in div_elem:
        if child.tag == "l":
            process_line_element(child, tokens)
        elif child.tag == "milestone":
            tokens.append(("milestone", child.attrib))
        # Ignore other tags at the top level.
    return tokens


def build_verses(tokens: list[Token], book_number: int) -> list[Verse]:
    verses: list[Verse] = []
    current_start: int | None = None
    current_paragraphs: list[list[str]] = []
    current_line_number: int | None = None

    def finalize(end_line: int) -> None:
        nonlocal current_start, current_paragraphs, current_line_number
        if current_start is None:
            return
        paragraphs = [p for p in current_paragraphs if p]
        if not paragraphs:
            paragraphs = [[]]
        verses.append(
            Verse(
                book=book_number,
                line_numbers=(current_start, end_line),
                paragraphs=paragraphs,
                corresponding=[],
            )
        )
        current_start = None
        current_paragraphs = []
        current_line_number = None

    for token in tokens:
        if is_milestone_token(token):
            unit = token[1].get("unit")
            if unit == "card":
                n = int(token[1]["n"])
                if current_start is not None and current_line_number is not None:
                    finalize(n - 1)
                current_start = n
                current_line_number = n
                current_paragraphs = [[]]
            elif unit == "para":
                if not current_paragraphs:
                    current_paragraphs = [[]]
                if current_paragraphs[-1]:
                    current_paragraphs.append([])
        elif is_line_token(token):
            if current_start is None:
                current_start = 1
                current_line_number = 1
                current_paragraphs = [[]]
            if not current_paragraphs:
                current_paragraphs = [[]]
            current_paragraphs[-1].append(token[1])
            if current_line_number is not None:
                current_line_number += 1

    if current_start is not None and current_line_number is not None:
        finalize(current_line_number - 1)

    return verses


def parse_book(path: Path) -> list[Verse]:
    tree = ET.parse(path)
    div = tree.find(".//div1")
    if div is None:
        raise ValueError(f"No <div1> element found in {path}")

    tokens = flatten_div(div)
    book_number = int(div.attrib.get("n", "0"))
    return build_verses(tokens, book_number)


def parse_collection(directory: Path) -> list[Verse]:
    verses: list[Verse] = []
    for xml_file in sorted(directory.glob("*.xml")):
        verses.extend(parse_book(xml_file))
    return verses


def ranges_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return not (a[1] < b[0] or b[1] < a[0])


def match_corresponding(latin: list[Verse], english: list[Verse]) -> None:
    english_by_book: dict[int, list[Verse]] = {}
    for verse in english:
        english_by_book.setdefault(verse.book, []).append(verse)

    for lat in latin:
        candidates = english_by_book.get(lat.book, [])
        for eng in candidates:
            if ranges_overlap(lat.line_numbers, eng.line_numbers):
                if eng not in lat.corresponding:
                    lat.corresponding.append(eng)
                if lat not in eng.corresponding:
                    eng.corresponding.append(lat)


def build_all() -> tuple[list[Verse], list[Verse]]:
    latin_dir = Path("resources/latin")
    english_dir = Path("resources/dryden")
    latin_verses = parse_collection(latin_dir)
    english_verses = parse_collection(english_dir)
    match_corresponding(latin_verses, english_verses)
    return latin_verses, english_verses


def _add_ids_and_links(
    latin: list[Verse], english: list[Verse]
) -> tuple[list[dict], list[dict]]:
    latin_ids = {id(v): f"L{idx}" for idx, v in enumerate(latin)}
    english_ids = {id(v): f"E{idx}" for idx, v in enumerate(english)}

    def serialize(
        verses: list[Verse], own_ids: dict[int, str], other_ids: dict[int, str]
    ) -> list[dict]:
        payload: list[dict] = []
        for verse in verses:
            payload.append(
                {
                    "book": verse.book,
                    "line_numbers": list(verse.line_numbers),
                    "paragraphs": verse.paragraphs,
                    "id": own_ids[id(verse)],
                    "correspondingIds": [other_ids[id(c)] for c in verse.corresponding],
                }
            )
        return payload

    latin_serialized = serialize(latin, latin_ids, english_ids)
    english_serialized = serialize(english, english_ids, latin_ids)
    return latin_serialized, english_serialized


def save_verses_json(latin: list[Verse], english: list[Verse]) -> None:
    latin_serialized, english_serialized = _add_ids_and_links(latin, english)
    Path("latin_verses.json").write_text(
        json.dumps(latin_serialized, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    Path("english_verses.json").write_text(
        json.dumps(english_serialized, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    latin, english = build_all()
    save_verses_json(latin, english)
    print(f"Latin verses: {len(latin)} -> latin_verses.json")
    print(f"English verses: {len(english)} -> english_verses.json")
