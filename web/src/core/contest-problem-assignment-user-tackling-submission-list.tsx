import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import { DateTime } from 'luxon';
import React from 'react';
import { Table } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ContestProblemAssignmentUserTacklingSubmissionListFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { useBasePath } from '../util/paths';
import { columnFragment, getTableClassByValence, recordFragment } from './field-table';
import { Field } from './fields/field';
import { Text, textFragment } from './text';

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
  const { t } = useTranslation();

  return (
    <Table hover striped responsive>
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
                {submission.officialEvaluation?.status === 'PENDING' && (
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
