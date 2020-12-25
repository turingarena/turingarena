import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import React from 'react';
import { Table } from 'react-bootstrap';
import { SubmissionFragment} from '../generated/graphql-types';
import { useT } from '../translations/main';
import { FragmentProps } from '../util/fragment-props';
import { columnFragment, getTableClassByValence, recordFragment } from './field-table';
import { Field } from './fields/field';
import { Text, textFragment } from './text';

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
  const t = useT();

  return (
    <>
      {data.officialEvaluation?.status === 'COMPILEERROR' ? (
        <div
          className={css`
            background-color: rgba(0, 0, 0, 0.1);
            text-align: center;
          `}
        >
          {t('compileError')}
        </div>
      ) : (
        <div></div>
      )}
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
        <FontAwesomeIcon icon="spinner" pulse /> {t('evaluating')}...
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
                <td key={`submission-table-${rowIndex}-${fieldIndex}`}>
                  <Field data={field} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
}
