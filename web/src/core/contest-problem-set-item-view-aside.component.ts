import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { ContestProblemSetItemViewAsideFragment } from '../generated/graphql-types';
import { gradingStateFragment } from './grading.component';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-contest-problem-set-item-view-aside',
  templateUrl: './contest-problem-set-item-view-aside.component.html',
  styleUrls: ['./contest-problem-set-item-view-aside.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemSetItemViewAsideComponent {
  @Input()
  data!: ContestProblemSetItemViewAsideFragment;
}

export const contestProblemSetItemViewAsideFragment = gql`
  fragment ContestProblemSetItemViewAside on ContestProblemSetItemView {
    item {
      problem {
        title {
          ...Text
        }
      }
    }
    gradingState {
      ...GradingState
    }
  }

  ${textFragment}
  ${gradingStateFragment}
`;
