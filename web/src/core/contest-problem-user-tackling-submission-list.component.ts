import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { ContestProblemUserTacklingSubmissionListFragment } from '../generated/graphql-types';
import { submissionModalFragment } from './submission-modal.component';

@Component({
  selector: 'app-contest-problem-user-tackling-submission-list',
  templateUrl: './contest-problem-user-tackling-submission-list.component.html',
  styleUrls: ['./contest-problem-user-tackling-submission-list.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemUserTacklingSubmissionListComponent {
  @Input()
  data!: ContestProblemUserTacklingSubmissionListFragment;
}

export const contestProblemUserTacklingSubmissionListFragment = gql`
  fragment ContestProblemUserTacklingSubmissionList on ContestProblemUserTackling {
    submissions {
      id
      createdAt
      # TODO: submission files
      officialEvaluation {
        status
      }

      ...SubmissionModal
    }
  }

  ${submissionModalFragment}
`;
