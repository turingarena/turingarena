import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { ScoreFieldFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-score-field',
  templateUrl: './score-field.component.html',
  encapsulation: ViewEncapsulation.None,
})
export class GradingNumericComponent {
  @Input()
  data!: ScoreFieldFragment;
}

export const scoreFieldFragment = gql`
  fragment ScoreField on ScoreField {
    scoreRange {
      max
      allowPartial
      decimalDigits
    }
    score
    valence
  }
`;
