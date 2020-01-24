import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { BooleanGradingStateFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-grading-boolean',
  templateUrl: './grading-boolean.component.html',
  encapsulation: ViewEncapsulation.None,
})
export class GradingBooleanComponent {
  @Input()
  data!: BooleanGradingStateFragment;
}

export const booleanGradingStateFragment = gql`
  fragment BooleanGradingState on BooleanGradingState {
    grade {
      value {
        achieved
      }
    }
  }
`;
