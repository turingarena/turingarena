import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { NumericGradingStateFragment } from '../generated/graphql-types';

@Component({
  selector: 'app-grading-numeric',
  templateUrl: './grading-numeric.component.html',
  encapsulation: ViewEncapsulation.None,
})
export class GradingNumericComponent {
  @Input()
  data!: NumericGradingStateFragment;
}

export const numericGradingStateFragment = gql`
  fragment NumericGradingState on NumericGradingState {
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
`;
