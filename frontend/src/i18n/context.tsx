"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

import { DICTIONARIES, type Lang, type TranslationKey } from "./dictionaries";

export type { Lang, Dictionary, TranslationKey } from "./dictionaries";

interface I18nContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: TranslationKey) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>("vi");

  const t = useCallback((key: TranslationKey) => DICTIONARIES[lang][key], [lang]);

  const value = useMemo(() => ({ lang, setLang, t }), [lang, t]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n phải dùng bên trong <I18nProvider>");
  return ctx;
}
