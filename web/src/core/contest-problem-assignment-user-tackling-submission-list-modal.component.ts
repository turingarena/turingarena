import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import gql from 'graphql-tag';
import { ContestProblemAssignmentUserTacklingSubmissionListModalFragment } from '../generated/graphql-types';
import { contestProblemAssignmentUserTacklingSubmissionListFragment } from './contest-problem-assignment-user-tackling-submission-list.component';
import { textFragment } from './material/text.pipe';

@Component({
  selector: 'app-contest-problem-assignment-user-tackling-submission-list-modal',
  templateUrl: './contest-problem-assignment-user-tackling-submission-list-modal.component.html',
  styleUrls: ['./contest-problem-assignment-user-tackling-submission-list-modal.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemAssignmentUserTacklingSubmissionListModalComponent {
  @Input()
  data!: ContestProblemAssignmentUserTacklingSubmissionListModalFragment;

  @Input()
  modal!: NgbActiveModal;
}

export const contestProblemAssignmentUserTacklingSubmissionListModalFragment = gql`
  fragment ContestProblemAssignmentUserTacklingSubmissionListModal on ContestProblemAssignmentUserTackling {
    assignmentView {
      assignment {
        problem {
          title {
            ...Text
          }
        }
      }
    }

    ...ContestProblemAssignmentUserTacklingSubmissionList
  }

  ${textFragment}
  ${contestProblemAssignmentUserTacklingSubmissionListFragment}
`;
