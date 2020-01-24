import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { GradingStateFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-grading',
  templateUrl: './grading.component.html',
  styleUrls: ['./grading.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class GradingComponent {
  @Input()
  data!: GradingStateFragment;
}

export const gradingStateFragment = gql`
  fragment GradingState on GradingState {
    __typename
    ... on GenericGradingState {
      valence
    }
    ... on BooleanGradingState {
      grade {
        value {
          achieved
        }
      }
      valence
    }
    ... on NumericGradingState {
      domain {
        max
        allowPartial
        decimalPrecision
      }
      grade {
        value {
          score
        }
      }
    }
  }
`;
