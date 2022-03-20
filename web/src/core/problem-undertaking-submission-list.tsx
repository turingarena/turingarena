import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import { DateTime } from 'luxon';
import React from 'react';
import { Table } from 'react-bootstrap';
import { FormattedMessage } from 'react-intl';
import { Link, useRouteMatch } from 'react-router-dom';
import { ProblemUndertakingSubmissionListFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { Field } from './data/field';
import { Text, textFragment } from './data/text';
import { columnFragment, getTableClassByValence, recordFragment } from './field-table';

export const problemUndertakingSubmissionListFragment = gql`
  fragment ProblemUndertakingSubmissionList on ProblemUndertaking {
    submissions {
      ...ProblemUndertakingSubmissionListSubmission
    }

    view {
      instance {
        definition {
          submissionListColumns {
            ...Column
          }
        }
      }
    }
  }

  fragment ProblemUndertakingSubmissionListSubmission on Submission {
    id
    createdAt {
      local
    }
    # TODO: submission files
    officialEvaluation {
      id
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

export function ProblemUndertakingSubmissionList({ data }: FragmentProps<ProblemUndertakingSubmissionListFragment>) {
  const { path } = useRouteMatch();

  return (
    <Table hover striped responsive style={{ marginBottom: 0 }}>
      <thead className="thead-light">
        <tr>
          <th>
            <FormattedMessage id="submission-submitted-at-column-header" defaultMessage="Submitted at" />
          </th>
          {data.view.instance.definition.submissionListColumns.map((col, index) => (
            <th key={`submission-header-${index}`}>
              <Text data={col.title} />
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.submissions.map((submission, submissionIndex) => (
          <tr key={`submission-${submissionIndex}`} className={getTableClassByValence(submission.summaryRow.valence)}>
            <td>
              <Link
                className={css`
                  display: flex;
                `}
                to={`${path.replace(/submissions$/, '')}submission/${submission.id}`}
              >
                {DateTime.fromISO(submission.createdAt.local).toRelative() ?? `${submission.createdAt.local}`}
                {submission.officialEvaluation === null && (
                  <span
                    className={css`
                      margin-left: auto;
                    `}
                  >
                    <FontAwesomeIcon icon="spinner" pulse />
                  </span>
                )}
              </Link>
            </td>
            {submission.summaryRow.fields.map((field, fieldIndex) => (
              <td key={`submission-${submissionIndex}-${fieldIndex}`}>{field && <Field data={field} />}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </Table>
  );
}
