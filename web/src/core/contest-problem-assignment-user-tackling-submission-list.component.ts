import { Component, Input, ViewEncapsulation } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ColDef } from 'ag-grid-community';
import gql from 'graphql-tag';
import { DateTime } from 'luxon';
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
  constructor(readonly modalService: NgbModal) {}

  @Input()
  data!: ContestProblemAssignmentUserTacklingSubmissionListFragment;

  openSubmission!: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment;

  getSummaryRows(submissions: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment[]) {
    return submissions.map(s => s.summaryRow);
  }

  getColumns(data: ContestProblemAssignmentUserTacklingSubmissionListFragment): ColDef[] {
    return [
      {
        colId: 'time',
        headerName: 'Submitted at',
        valueGetter: ({ data: submission }) =>
          (submission as ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment).createdAt.local,
        valueFormatter: ({ value: dateString }) =>
          DateTime.fromISO(dateString as string).toRelative() ?? `${dateString}`,
        tooltipValueGetter: ({ value: dateString }) => `${dateString}`.replace('T', ' '),
      },
      ...getFieldColumns(
        data.assignmentView.assignment.problem.submissionListColumns,
        (submission: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment) => submission.summaryRow,
      ),
    ];
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
