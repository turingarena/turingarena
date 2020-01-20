import { Injectable, Injector, LOCALE_ID } from '@angular/core';
import { TextFragment, VariantAttributeFragment } from '../generated/graphql-types';

@Injectable({
  providedIn: 'root',
})
export class VariantService {
  // FIXME: avoiding @Inject to make Babel happier
  private readonly locale: string;
  constructor(injector: Injector) {
    this.locale = injector.get(LOCALE_ID);
  }

  selectVariant<T extends { attributes: VariantAttributeFragment[] }>(variants: T[], style?: string): T {
    const styleScore = 10;
    const languageScore = 5;
    const sortedVariants = variants.slice();

    sortedVariants.sort((a, b) => {
      const [aScore, bScore] = [a, b].map(
        v =>
          (v.attributes.some(({ key, value }) => key === 'style' && value === style) ? styleScore : 0) +
          (v.attributes.some(({ key, value }) => key === 'locale' && value === this.locale) ? languageScore : 0),
      );

      return bScore - aScore;
    });

    return sortedVariants[0];
  }

  selectTextVariant(variants: TextFragment[], style?: string) {
    return this.selectVariant(variants, style).value;
  }
}
