import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import { ContestProblemUserTacklingSubmissionListModalFragment } from '../generated/graphql-types';
import { contestProblemUserTacklingSubmissionListFragment } from './contest-problem-user-tackling-submission-list.component';
import { textFragment } from './text.pipe';

@Component({
  selector: 'app-contest-problem-user-tackling-submission-list-modal',
  templateUrl: './contest-problem-user-tackling-submission-list-modal.component.html',
  styleUrls: ['./contest-problem-user-tackling-submission-list-modal.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemUserTacklingSubmissionListModalComponent {
  @Input()
  data!: ContestProblemUserTacklingSubmissionListModalFragment;

  @Input()
  modal!: NgbActiveModal;
}

export const contestProblemUserTacklingSubmissionListModalFragment = gql`
  fragment ContestProblemUserTacklingSubmissionListModal on ContestProblemUserTackling {
    assignmentView {
      assignment {
        problem {
          title {
            ...Text
          }
        }
      }
    }

    ...ContestProblemUserTacklingSubmissionList
  }

  ${textFragment}
  ${contestProblemUserTacklingSubmissionListFragment}
`;
