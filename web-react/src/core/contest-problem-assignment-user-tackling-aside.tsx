import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import React from 'react';
import { ContestProblemAssignmentUserTacklingAsideFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';
import { contestProblemAssignmentUserTacklingSubmissionListModalFragment } from './contest-problem-assignment-user-tackling-submission-list-modal';
import { contestProblemAssignmentUserTacklingSubmitModalFragment } from './contest-problem-assignment-user-tackling-submit-modal';
import { submissionModalFragment } from './submission-modal';

export const contestProblemAssignmentUserTacklingAsideFragment = gql`
  fragment ContestProblemAssignmentUserTacklingAside on ContestProblemAssignmentUserTackling {
    canSubmit
    submissions {
      id
      officialEvaluation {
        status
      }

      ...SubmissionModal
    }

    ...ContestProblemAssignmentUserTacklingSubmitModal
    ...ContestProblemAssignmentUserTacklingSubmissionListModal
  }

  ${submissionModalFragment}
  ${contestProblemAssignmentUserTacklingSubmitModalFragment}
  ${contestProblemAssignmentUserTacklingSubmissionListModalFragment}
`;

export function ContestProblemAssignmentUserTacklingAside({
  data,
}: FragmentProps<ContestProblemAssignmentUserTacklingAsideFragment>) {
  const lastSubmission = data.submissions.length > 0 ? data.submissions[data.submissions.length - 1] : null;

  return (
    <>
      {data.canSubmit && (
        <button className="btn btn-block btn-success">
          <FontAwesomeIcon icon="paper-plane" />
          Submit a solution
        </button>
      )}

      {lastSubmission !== null && (
        <>
          <button className="btn btn-block btn-outline">
            {lastSubmission.officialEvaluation?.status === 'PENDING' && <FontAwesomeIcon icon="history" />}
            {lastSubmission.officialEvaluation?.status !== 'PENDING' && <FontAwesomeIcon icon="spinner" pulse={true} />}
            Last submission
          </button>
          <button className="btn btn-block btn-outline">
            <FontAwesomeIcon icon="list" />
            All submissions
          </button>
        </>
      )}
    </>
  );
}
