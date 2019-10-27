import { Pipe, PipeTransform, LOCALE_ID, Inject } from '@angular/core';
import { TextFragment } from './__generated__/TextFragment';

export interface AttributeLookup {
  key: string;
  value: string;
}

@Pipe({
  name: 'textVariant'
})
export class TextVariantPipe implements PipeTransform {

  constructor(
    @Inject(LOCALE_ID) readonly locale: string,
  ) { }

  transform(variants: TextFragment[], style?: string): string {
    const sortedVariants = variants.slice();
    sortedVariants.sort((a, b) => {
      const [aScore, bScore] = [a, b].map((v) =>
        (v.attributes.find(({ key, value }) => key === 'style' && value === style) ? 10 : 0)
        +
        (v.attributes.find(({ key, value }) => key === 'locale' && value === this.locale) ? 5 : 0)
      );
      return bScore - aScore;
    });
    return sortedVariants[0].value;
  }

}
