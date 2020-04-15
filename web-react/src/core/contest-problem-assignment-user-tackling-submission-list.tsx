import { gql } from '@apollo/client';
import { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { DateTime } from 'luxon';
import React from 'react';
import {
  ContestProblemAssignmentUserTacklingSubmissionListFragment,
  ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment,
} from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { getFieldColumns } from './field-table';
import { submissionModalFragment } from './submission-modal';
import { textFragment } from './text';

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

export function ContestProblemAssignmentUserTacklingSubmissionList({
  data,
}: FragmentProps<ContestProblemAssignmentUserTacklingSubmissionListFragment>) {
  const columns: ColDef[] = [
    {
      colId: 'time',
      headerName: 'Submitted at',
      sortable: true,
      sort: 'desc',
      sortingOrder: ['desc', 'asc', null] as string[],
      valueGetter: ({
        data: submission,
      }: {
        data: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment;
      }) => submission.createdAt.local,
      valueFormatter: ({ value: dateString }: { value: string }) =>
        DateTime.fromISO(dateString).toRelative() ?? `${dateString}`,
      tooltipValueGetter: ({ value: dateString }: { value?: string }) => `${dateString ?? ''}`.replace('T', ' '),
    },
    ...getFieldColumns(
      data.assignmentView.assignment.problem.submissionListColumns,
      (submission: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment) => submission.summaryRow,
    ),
  ];

  return <AgGridReact domLayout="autoHeight" columnDefs={columns} rowData={data.submissions} />;
}
