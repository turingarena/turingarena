import { Resource, TOptions } from 'i18next';
import { useTranslation } from 'react-i18next';
import { en } from './en';

export type TransationKey = keyof typeof en.translation;
export type TranslationObject = {
  translation: Partial<Record<TransationKey, string>>;
} & Resource;

export function useT() {
  const { t } = useTranslation();

  return t as (key: TransationKey | TransationKey[], options?: TOptions | string) => string;
}
