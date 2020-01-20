import { Pipe, PipeTransform } from '@angular/core';
import { FileFragment } from '../generated/graphql-types';
import { VariantService } from './variant.service';

@Pipe({
  name: 'fileVariant',
})
export class FileVariantPipe implements PipeTransform {
  constructor(readonly variantService: VariantService) {}

  transform(variants: FileFragment[], style?: string) {
    return this.variantService.selectVariant(variants, style);
  }
}
