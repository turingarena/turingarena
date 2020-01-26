import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { GradeVariableFragment } from '../../generated/graphql-types';
import { booleanGradeVariableFragment } from './fulfillment-variable.component';
import { numericGradeVariableFragment } from './score-variable.component';

@Component({
  selector: 'app-grade-variable',
  templateUrl: './grade-variable.component.html',
  styleUrls: ['./grade-variable.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class GradingComponent {
  @Input()
  data!: GradeVariableFragment;
}

export const gradeVariableFragment = gql`
  fragment GradeVariable on GradeVariable {
    __typename
    ... on GenericGradeVariable {
      value {
        valence
      }
    }
    ... on FulfillmentVariable {
      ...FulfillmentVariable
    }
    ... on ScoreVariable {
      ...ScoreVariable
    }
  }

  ${numericGradeVariableFragment}
  ${booleanGradeVariableFragment}
`;
