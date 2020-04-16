import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { AgGridReact } from 'ag-grid-react';
import { css, cx } from 'emotion';
import React from 'react';
import { RecordFragment, SubmissionFragment } from '../generated/graphql-types';
import { gridCss } from '../util/components/grid';
import { FragmentProps } from '../util/fragment-props';
import { columnFragment, getFieldColumns, recordFragment } from './field-table';
import { textFragment } from './text';

export const submissionFragment = gql`
  fragment Submission on Submission {
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

export function Submission({ data }: FragmentProps<SubmissionFragment>) {
  const rowData = JSON.parse(JSON.stringify(data.feedbackTable.rows)) as typeof data.feedbackTable.rows; // allow AgGrid to mess with this data

  return (
    <>
      <div
        className={
          data.officialEvaluation?.status === 'PENDING'
            ? css`
                background-color: rgba(0, 0, 0, 0.1);
                text-align: center;
              `
            : css`
                display: none;
              `
        }
      >
        <FontAwesomeIcon icon="spinner" pulse /> Evaluating...
      </div>
      <div className={cx(gridCss)}>
        <AgGridReact
          columnDefs={getFieldColumns(data.feedbackTable.columns, (row: RecordFragment) => row)}
          domLayout="autoHeight"
          rowData={rowData}
        />
      </div>
    </>
  );
}
