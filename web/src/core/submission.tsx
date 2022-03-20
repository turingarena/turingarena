import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import React from 'react';
import { Table } from 'react-bootstrap';
import { FormattedMessage } from 'react-intl';
import { SubmissionFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { Field } from './data/field';
import { Text, textFragment } from './data/text';
import { columnFragment, getTableClassByValence, recordFragment } from './field-table';

export const submissionFragment = gql`
  fragment Submission on Submission {
    id
    # TODO: files
    createdAt {
      local
    }
    officialEvaluation {
      id
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
  return (
    <>
      {
        /* TODO: compile error */ false && (
          <div
            className={css`
              background-color: rgba(0, 0, 0, 0.1);
              text-align: center;
            `}
          >
            Compilation error
          </div>
        )
      }
      <div
        className={
          data.officialEvaluation === null
            ? css`
                background-color: rgba(0, 0, 0, 0.1);
                text-align: center;
              `
            : css`
                display: none;
              `
        }
      >
        <FontAwesomeIcon icon="spinner" pulse />{' '}
        <FormattedMessage id="submission-evaluating-message" defaultMessage="Evaluating..." />
      </div>
      <Table hover responsive striped style={{ marginBottom: 0 }}>
        <thead className="thead-light">
          <tr>
            {data.feedbackTable.columns.map((col, colIndex) => (
              <th key={`submission-table-col-${colIndex}`}>
                <Text data={col.title} />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.feedbackTable.rows.map((row, rowIndex) => (
            <tr key={`submission-table-${rowIndex}`} className={getTableClassByValence(row.valence)}>
              {row.fields.map((field, fieldIndex) => (
                <td key={`submission-table-${rowIndex}-${fieldIndex}`}>{field && <Field data={field} />}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
}
