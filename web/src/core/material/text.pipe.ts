import { Pipe, PipeTransform } from '@angular/core';
import gql from 'graphql-tag';
import { TextFragment } from '../../generated/graphql-types';

@Pipe({
  name: 'text',
})
export class TextPipe implements PipeTransform {
  transform(value: TextFragment): string {
    return value.variant;
  }
}

export const textFragment = gql`
  fragment Text on Text {
    variant
  }
`;
