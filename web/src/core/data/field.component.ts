import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { FieldFragment } from '../../generated/graphql-types';
import { fulfillmentFieldFragment } from '../grading/fulfillment-field.component';
import { scoreFieldFragment } from '../grading/score-field.component';
import { indexFieldFragment } from './index-field.component';
import { memoryUsageFieldFragment } from './memory-usage-field.component';
import { messageFieldFragment } from './message-field.component';
import { timeUsageFieldFragment } from './time-usage-field.component';
import { titleFieldFragment } from './title-field.component';

@Component({
  selector: 'app-field',
  templateUrl: './field.component.html',
  styleUrls: ['./field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class FieldComponent {
  @Input()
  data!: FieldFragment;
}

export const fieldFragment = gql`
  fragment Field on Field {
    ... on FulfillmentField {
      ...FulfillmentField
    }
    ... on ScoreField {
      ...ScoreField
    }
    ... on IndexField {
      ...IndexField
    }
    ... on TitleField {
      ...TitleField
    }
    ... on MessageField {
      ...MessageField
    }
    ... on TimeUsageField {
      ...TimeUsageField
    }
    ... on MemoryUsageField {
      ...MemoryUsageField
    }
  }

  ${fulfillmentFieldFragment}
  ${scoreFieldFragment}
  ${indexFieldFragment}
  ${memoryUsageFieldFragment}
  ${messageFieldFragment}
  ${timeUsageFieldFragment}
  ${titleFieldFragment}
`;
