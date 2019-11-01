import { Inject, LOCALE_ID, Pipe, PipeTransform } from '@angular/core';

import { TextFragment } from './__generated__/TextFragment';

export interface AttributeLookup {
  key: string;
  value: string;
}

@Pipe({
  name: 'textVariant',
})
export class TextVariantPipe implements PipeTransform {

  constructor(
    @Inject(LOCALE_ID) readonly locale: string,
  ) { }

  transform(variants: TextFragment[], style?: string): string {
    const styleScore = 10;
    const languageScore = 5;
    const sortedVariants = variants.slice();

    sortedVariants.sort((a, b) => {
      const [aScore, bScore] = [a, b].map((v) =>
        (v.attributes.some(({ key, value }) => key === 'style' && value === style) ? styleScore : 0)
        +
        (v.attributes.some(({ key, value }) => key === 'locale' && value === this.locale) ? languageScore : 0),
      );

      return bScore - aScore;
    });

    return sortedVariants[0].value;
  }

}
