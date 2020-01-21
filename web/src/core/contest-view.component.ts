import { Component, Input } from '@angular/core';
import gql from 'graphql-tag';
import { ContestViewFragment } from '../generated/graphql-types';
import { gradingStateFragment } from './grading.component';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-contest-view',
  templateUrl: './contest-view.component.html',
  styleUrls: ['./contest-view.component.scss'],
})
export class ContestViewComponent {
  @Input()
  data!: ContestViewFragment;
}

export const contestViewFragment = gql`
  fragment ContestView on ContestView {
    contest {
      title {
        variant
      }
      start
      end
      status
    }

    problemSetView {
      itemViews {
        item {
          problem {
            name
            title {
              ...Text
            }
          }
        }
        gradingState {
          ...GradingState
        }
      }
      gradingState {
        ...GradingState
      }
    }
  }

  ${textFragment}
  ${gradingStateFragment}
`;
