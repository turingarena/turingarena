import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { TitleFieldFragment } from '../../generated/graphql-types';
import { textFragment } from '../material/text.pipe';

@Component({
  selector: 'app-title-field',
  templateUrl: './title-field.component.html',
  styleUrls: ['./title-field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class TitleFieldComponent {
  @Input()
  data!: TitleFieldFragment;
}

export const titleFieldFragment = gql`
  fragment TitleField on TitleField {
    title {
      ...Text
    }
  }

  ${textFragment}
`;
