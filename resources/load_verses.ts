import { readFile } from "fs/promises";
import { resolve } from "path";

type VerseJSON = {
  book: number;
  line_numbers: [number, number];
  paragraphs: string[][];
  id: string;
  correspondingIds: string[];
};

export type Verse = {
  book: number;
  line_numbers: [number, number];
  paragraphs: string[][];
  id: string;
  correspondingIds: string[];
  corresponding: Verse[];
};

async function readJson(pathLike: string): Promise<VerseJSON[]> {
  const fullPath = resolve(pathLike);
  const raw = await readFile(fullPath, "utf-8");
  return JSON.parse(raw) as VerseJSON[];
}

function hydrate(raw: VerseJSON[]): Verse[] {
  return raw.map((v) => ({
    ...v,
    corresponding: [],
  }));
}

function attachCorresponding(source: Verse[], targetById: Map<string, Verse>) {
  source.forEach((verse) => {
    verse.correspondingIds.forEach((cid) => {
      const other = targetById.get(cid);
      if (!other) return;
      if (!verse.corresponding.includes(other)) {
        verse.corresponding.push(other);
      }
      if (!other.corresponding.includes(verse)) {
        other.corresponding.push(verse);
      }
    });
  });
}

export async function loadVersesJSON(
  latinPath = "latin_verses.json",
  englishPath = "english_verses.json"
): Promise<{ latin: Verse[]; english: Verse[] }> {
  const [latinRaw, englishRaw] = await Promise.all([
    readJson(latinPath),
    readJson(englishPath),
  ]);

  const latin = hydrate(latinRaw);
  const english = hydrate(englishRaw);

  const latinById = new Map(latin.map((v) => [v.id, v] as const));
  const englishById = new Map(english.map((v) => [v.id, v] as const));

  attachCorresponding(latin, englishById);
  attachCorresponding(english, latinById);

  return { latin, english };
}
