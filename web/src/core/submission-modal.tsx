import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { AgGridReact } from 'ag-grid-react';
import { css, cx } from 'emotion';
import React from 'react';
import { RecordFragment, SubmissionModalFragment } from '../generated/graphql-types';
import { buttonCss, buttonPrimaryCss } from '../util/components/button';
import { gridCss } from '../util/components/grid';
import { modalFooterCss, modalHeaderCss } from '../util/components/modal';
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
    <>
      <div
        className={css`
          width: 80vw;
          overflow: auto;
        `}
      >
        <div className={modalHeaderCss}>
          <h5>
            {/* TODO: submission index, e.g., Submission #6 for: My Problem */}
            Submission for: <strong>{data.problem.title.variant}</strong>
          </h5>
        </div>
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
            rowData={data.feedbackTable.rows}
          />
        </div>
        <div className={modalFooterCss}>
          <button onClick={() => {}} className={cx(buttonCss, buttonPrimaryCss)}>
            Close
          </button>
        </div>
      </div>
    </>
  );
}
