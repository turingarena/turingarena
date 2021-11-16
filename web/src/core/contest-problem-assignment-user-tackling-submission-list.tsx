import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import { DateTime } from 'luxon';
import React from 'react';
import { Table } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ProblemTacklingSubmissionListFragment } from '../generated/graphql-types';
import { useT } from '../translations/main';
import { FragmentProps } from '../util/fragment-props';
import { useBasePath } from '../util/paths';
import { columnFragment, getTableClassByValence, recordFragment } from './field-table';
import { Field } from './fields/field';
import { Text, textFragment } from './text';

export const problemTacklingSubmissionListFragment = gql`
  fragment ProblemTacklingSubmissionList on ProblemTackling {
    submissions {
      ...ProblemTacklingSubmissionListSubmission
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

  fragment ProblemTacklingSubmissionListSubmission on Submission {
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

export function ProblemTacklingSubmissionList({
  data,
}: FragmentProps<ProblemTacklingSubmissionListFragment>) {
  const basePath = useBasePath();
  const t = useT();

  return (
    <Table hover striped responsive style={{ marginBottom: 0 }}>
      <thead className="thead-light">
        <tr>
          <th>{t('submittedAt')}</th>
          {data.assignmentView.assignment.problem.submissionListColumns.map((col, index) => (
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
                to={`${basePath}/submission/${submission.id}`}
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
              <td key={`submission-${submissionIndex}-${fieldIndex}`}>
                <Field data={field} />
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </Table>
  );
}
