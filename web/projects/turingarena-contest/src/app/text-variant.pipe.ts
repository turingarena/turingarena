import { Pipe, PipeTransform } from '@angular/core';

import { TextFragment } from './__generated__/TextFragment';
import { VariantService } from './variant.service';

export interface AttributeLookup {
  key: string;
  value: string;
}

@Pipe({
  name: 'textVariant',
})
export class TextVariantPipe implements PipeTransform {
  constructor(readonly variantService: VariantService) { }

  transform(variants: TextFragment[], style?: string) {
    const variant = this.variantService.selectVariant(variants, style);

    return variant !== undefined ? variant.value : '';
  }
}
