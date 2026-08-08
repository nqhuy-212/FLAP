import en from "./en.json";
import vi from "./vi.json";

export type Lang = "vi" | "en";
export type Dictionary = typeof vi;
export type TranslationKey = keyof Dictionary;

export const DICTIONARIES: Record<Lang, Dictionary> = { vi, en };

export function isLang(value: string | null): value is Lang {
  return value === "vi" || value === "en";
}

/** Dùng cho route không tương tác (TV) — ngôn ngữ cố định từ URL, không có Context. */
export function getDictionary(lang: Lang): Dictionary {
  return DICTIONARIES[lang];
}
