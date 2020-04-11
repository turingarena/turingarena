import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import {
  ContestProblemAssignmentUserTacklingSubmissionListFragment,
  ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment,
} from '../generated/graphql-types';
import { getFieldColumns } from './data/field-table';
import { textFragment } from './material/text.pipe';
import { submissionModalFragment } from './submission-modal.component';

@Component({
  selector: 'app-contest-problem-assignment-user-tackling-submission-list',
  templateUrl: './contest-problem-assignment-user-tackling-submission-list.component.html',
  styleUrls: ['./contest-problem-assignment-user-tackling-submission-list.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ContestProblemAssignmentUserTacklingSubmissionListComponent {
  @Input()
  data!: ContestProblemAssignmentUserTacklingSubmissionListFragment;

  getSummaryRows(submissions: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment[]) {
    return submissions.map(s => s.summaryRow);
  }

  getColumns(data: ContestProblemAssignmentUserTacklingSubmissionListFragment) {
    return getFieldColumns(
      data.assignmentView.assignment.problem.submissionListColumns,
      (submission: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment) => submission.summaryRow,
    );
  }
}

export const contestProblemAssignmentUserTacklingSubmissionListFragment = gql`
  fragment ContestProblemAssignmentUserTacklingSubmissionList on ContestProblemAssignmentUserTackling {
    submissions {
      ...ContestProblemAssignmentUserTacklingSubmissionListSubmission
    }

    assignmentView {
      assignment {
        problem {
          submissionListColumns {
            ...Column
          }
        }
      }
    }
  }

  fragment ContestProblemAssignmentUserTacklingSubmissionListSubmission on Submission {
    id
    createdAt {
      local
    }
    # TODO: submission files
    officialEvaluation {
      status
    }
    summaryRow {
      ...Record
    }

    feedbackTable {
      columns {
        ...Column
      }
      rows {
        ...Record
      }
    }

    ...SubmissionModal
  }

  ${submissionModalFragment}
  ${textFragment}
`;
