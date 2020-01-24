import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import { ContestProblemUserTacklingAsideFragment } from '../generated/graphql-types';
import { contestProblemUserTacklingSubmissionListModalFragment } from './contest-problem-user-tackling-submission-list-modal.component';
import { contestProblemUserTacklingSubmitModalFragment } from './contest-problem-user-tackling-submit-modal.component';
import { submissionModalFragment } from './submission-modal.component';

@Component({
  selector: 'app-contest-problem-user-tackling-aside',
  templateUrl: './contest-problem-user-tackling-aside.component.html',
  styleUrls: ['./contest-problem-user-tackling-aside.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemUserTacklingAsideComponent {
  constructor(readonly modalService: NgbModal) {}

  @Input()
  data!: ContestProblemUserTacklingAsideFragment;
}

export const contestProblemUserTacklingAsideFragment = gql`
  fragment ContestProblemUserTacklingAside on ContestProblemUserTackling {
    canSubmit
    submissions {
      id
      officialEvaluation {
        status
      }

      ...SubmissionModal
    }

    ...ContestProblemUserTacklingSubmitModal
    ...ContestProblemUserTacklingSubmissionListModal
  }

  ${submissionModalFragment}
  ${contestProblemUserTacklingSubmitModalFragment}
  ${contestProblemUserTacklingSubmissionListModalFragment}
`;
