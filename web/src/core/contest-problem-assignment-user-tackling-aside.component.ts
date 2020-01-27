import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import { ContestProblemAssignmentUserTacklingAsideFragment } from '../generated/graphql-types';
import { contestProblemAssignmentUserTacklingSubmissionListModalFragment } from './contest-problem-assignment-user-tackling-submission-list-modal.component';
import { contestProblemAssignmentUserTacklingSubmitModalFragment } from './contest-problem-assignment-user-tackling-submit-modal.component';
import { submissionModalFragment } from './submission-modal.component';

@Component({
  selector: 'app-contest-problem-assignment-user-tackling-aside',
  templateUrl: './contest-problem-assignment-user-tackling-aside.component.html',
  styleUrls: ['./contest-problem-assignment-user-tackling-aside.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemAssignmentUserTacklingAsideComponent {
  constructor(readonly modalService: NgbModal) {}

  @Input()
  data!: ContestProblemAssignmentUserTacklingAsideFragment;
}

export const contestProblemAssignmentUserTacklingAsideFragment = gql`
  fragment ContestProblemAssignmentUserTacklingAside on ContestProblemAssignmentUserTackling {
    canSubmit
    submissions {
      id
      officialEvaluation {
        status
      }

      ...SubmissionModal
    }

    ...ContestProblemAssignmentUserTacklingSubmitModal
    ...ContestProblemAssignmentUserTacklingSubmissionListModal
  }

  ${submissionModalFragment}
  ${contestProblemAssignmentUserTacklingSubmitModalFragment}
  ${contestProblemAssignmentUserTacklingSubmissionListModalFragment}
`;
