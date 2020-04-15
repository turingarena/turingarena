import { gql } from '@apollo/client';
import { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { css } from 'emotion';
import { DateTime } from 'luxon';
import React from 'react';
import { Link } from 'react-router-dom';
import {
  ContestProblemAssignmentUserTacklingSubmissionListFragment,
  ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment,
} from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { useBasePath } from '../util/paths';
import { columnFragment, getFieldColumns, recordFragment } from './field-table';
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
  }

  ${textFragment}
  ${columnFragment}
  ${recordFragment}
`;

export function ContestProblemAssignmentUserTacklingSubmissionList({
  data,
}: FragmentProps<ContestProblemAssignmentUserTacklingSubmissionListFragment>) {
  const basePath = useBasePath();

  const columns: ColDef[] = [
    {
      colId: 'time',
      headerName: 'Submitted at',
      sortable: true,
      sort: 'desc',
      sortingOrder: ['desc', 'asc', null] as string[],
      flex: 1,
      valueGetter: ({
        data: submission,
      }: {
        data: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment;
      }) => submission.createdAt.local,
      tooltipValueGetter: ({ value: dateString }: { value?: string }) => `${dateString ?? ''}`.replace('T', ' '),
      cellRendererFramework: ({
        data: submission,
      }: {
        data: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment;
      }) => (
        <Link
          className={css`
            display: block;
          `}
          to={`${basePath}/submission/${submission.id}`}
        >
          {DateTime.fromISO(submission.createdAt.local).toRelative() ?? `${submission.createdAt.local}`}
        </Link>
      ),
    },
    ...getFieldColumns(
      data.assignmentView.assignment.problem.submissionListColumns,
      (submission: ContestProblemAssignmentUserTacklingSubmissionListSubmissionFragment) => submission.summaryRow,
    ),
  ];

  return <AgGridReact domLayout="autoHeight" columnDefs={columns} rowData={data.submissions} />;
}
