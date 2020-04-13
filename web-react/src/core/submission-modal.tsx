import { gql } from '@apollo/client';
import { AgGridReact } from 'ag-grid-react';
import React from 'react';
import { RecordFragment, SubmissionModalFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { columnFragment, getFieldColumns, recordFragment } from './field-table';
import { textFragment } from './text';

export const submissionModalFragment = gql`
  fragment SubmissionModal on Submission {
    id
    # TODO: files
    createdAt {
      local
    }
    officialEvaluation {
      status
    }
    problem {
      id
      title {
        ...Text
      }
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
  ${recordFragment}
  ${columnFragment}
`;

export function SubmissionModal({ data }: FragmentProps<SubmissionModalFragment>) {
  return (
    <AgGridReact
      columnDefs={getFieldColumns(data.feedbackTable.columns, (row: RecordFragment) => row)}
      domLayout="autoHeight"
      rowData={data.feedbackTable.rows}
    />
  );
}
