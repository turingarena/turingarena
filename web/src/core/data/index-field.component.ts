import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { IndexFieldFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-index-field',
  templateUrl: './index-field.component.html',
  styleUrls: ['./index-field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class IndexFieldComponent {
  @Input()
  data!: IndexFieldFragment;
}

export const indexFieldFragment = gql`
  fragment IndexField on IndexField {
    index
  }
`;
