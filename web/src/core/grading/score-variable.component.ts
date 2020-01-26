import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { ScoreVariableFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-score-variable',
  templateUrl: './score-variable.component.html',
  encapsulation: ViewEncapsulation.None,
})
export class GradingNumericComponent {
  @Input()
  data!: ScoreVariableFragment;
}

export const numericGradeVariableFragment = gql`
  fragment ScoreVariable on ScoreVariable {
    domain {
      max
      allowPartial
      decimalDigits
    }
    value {
      score
    }
  }
`;
