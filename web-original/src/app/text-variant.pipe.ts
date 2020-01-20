import { Pipe, PipeTransform } from '@angular/core';
import { TextFragment } from '../generated/graphql-types';
import { VariantService } from './variant.service';

export interface AttributeLookup {
  key: string;
  value: string;
}

@Pipe({
  name: 'textVariant',
})
export class TextVariantPipe implements PipeTransform {
  constructor(readonly variantService: VariantService) {}

  transform(variants: TextFragment[], style?: string) {
    return this.variantService.selectTextVariant(variants, style);
  }
}
