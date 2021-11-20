import { MessageFormatElement } from '@formatjs/icu-messageformat-parser';
import React, { createContext, ReactNode, useContext, useEffect, useMemo, useState } from 'react';
import { IntlProvider } from 'react-intl';
import en from '../lang/en.json';
import it from '../lang/it.json';
import { fail } from './check';

const supportedMessages = { it, en };
const messages: Record<string, Record<string, MessageFormatElement[]>> = supportedMessages;

const supportedLocales = new Set(Object.keys(messages));

export type SupportedLanguage = keyof typeof supportedMessages;
const defaultLocale: SupportedLanguage = 'en';

export const supportedLanguageList = [...Object.keys(messages)] as SupportedLanguage[];

interface LanguageSettings {
  autoLanguage: SupportedLanguage;
  overrideLanguage: SupportedLanguage | null;
  setOverrideLanguage: (value: SupportedLanguage | null) => void;
}

const languageSettingsContext = createContext<LanguageSettings | null>(null);

export function AppIntlProvider({ children }: { children: ReactNode }) {
  const [autoLanguage, setAutoLanguage] = useState(getLanguage());
  const [overrideLanguage, setOverrideLanguage] = useState<SupportedLanguage | null>(null);

  const context = useMemo(
    (): LanguageSettings => ({
      autoLanguage,
      overrideLanguage,
      setOverrideLanguage,
    }),
    [autoLanguage, overrideLanguage],
  );

  useEffect(() => {
    const handleLanguageChange = () => {
      setAutoLanguage(getLanguage());
    };

    window.addEventListener('languagechange', handleLanguageChange);

    return () => {
      window.removeEventListener('languagechange', handleLanguageChange);
    };
  });

  const language = overrideLanguage ?? autoLanguage;

  return (
    <languageSettingsContext.Provider value={context}>
      <IntlProvider defaultLocale={defaultLocale} locale={language} messages={messages[language]}>
        {children}
      </IntlProvider>
    </languageSettingsContext.Provider>
  );
}

function getLanguage() {
  const languages = navigator.languages ?? [];

  return (languages.find(locale => supportedLocales.has(locale)) ?? defaultLocale) as SupportedLanguage;
}

export function useLanguageSettings() {
  return useContext(languageSettingsContext) ?? fail();
}
