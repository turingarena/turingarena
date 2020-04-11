import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { ContestViewAsideFragment } from '../generated/graphql-types';
import { contestViewClockFragment } from './contest-view-clock.component';
import { scoreFieldFragment } from './grading/score-field.component';
import { textFragment } from './material/text.pipe';

@Component({
  selector: 'app-contest-view-aside',
  templateUrl: './contest-view-aside.component.html',
  styleUrls: ['./contest-view-aside.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestViewAsideComponent {
  @Input()
  data!: ContestViewAsideFragment;
}

export const contestViewAsideFragment = gql`
  fragment ContestViewAside on ContestView {
    problemSetView {
      totalScoreField {
        ...ScoreField
      }

      assignmentViews {
        assignment {
          problem {
            name
            title {
              ...Text
            }
          }
        }
        totalScoreField {
          ...ScoreField
        }
      }
    }

    ...ContestViewClock
  }

  ${textFragment}
  ${scoreFieldFragment}
  ${contestViewClockFragment}
`;
