import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { GradeFieldFragment } from '../../generated/graphql-types';
import { fulfillmentFieldFragment } from './fulfillment-field.component';
import { scoreFieldFragment } from './score-field.component';

@Component({
  selector: 'app-grade-field',
  templateUrl: './grade-field.component.html',
  styleUrls: ['./grade-field.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class GradingComponent {
  @Input()
  data!: GradeFieldFragment;
}

export const gradeFieldFragment = gql`
  fragment GradeField on GradeField {
    __typename
    ... on FulfillmentField {
      ...FulfillmentField
    }
    ... on ScoreField {
      ...ScoreField
    }
  }

  ${scoreFieldFragment}
  ${fulfillmentFieldFragment}
`;
