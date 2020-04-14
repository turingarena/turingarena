import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { cx } from 'emotion';
import React, { useState } from 'react';
import { ContestProblemAssignmentUserTacklingAsideFragment } from '../generated/graphql-types';
import { buttonCss, buttonLightCss, buttonPrimaryCss } from '../util/components/button';
import { Modal } from '../util/components/modal';
import { FragmentProps } from '../util/fragment-props';
import { contestProblemAssignmentUserTacklingSubmissionListModalFragment } from './contest-problem-assignment-user-tackling-submission-list-modal';
import {
  ContestProblemAssignmentUserTacklingSubmitModal,
  contestProblemAssignmentUserTacklingSubmitModalFragment,
} from './contest-problem-assignment-user-tackling-submit-modal';
import { SubmissionModal, submissionModalFragment } from './submission-modal';

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
  const [showSubmitModal, setShowSubmitModal] = useState(false); // TODO: change to use routing instead
  const [showLastSubmissionModal, setShowLastSubmissionModal] = useState(false); // TODO: change to use routing instead

  const lastSubmission = data.submissions.length > 0 ? data.submissions[data.submissions.length - 1] : null;

  return (
    <>
      {data.canSubmit && (
        <>
          <button onClick={() => setShowSubmitModal(true)} className={cx(buttonCss, buttonPrimaryCss)}>
            <FontAwesomeIcon icon="paper-plane" />
            Submit a solution
          </button>
          <Modal show={showSubmitModal} onClose={() => setShowSubmitModal(false)}>
            <ContestProblemAssignmentUserTacklingSubmitModal data={data} />
          </Modal>
        </>
      )}

      {lastSubmission !== null && (
        <>
          <button onClick={() => setShowLastSubmissionModal(true)} className={cx(buttonCss, buttonLightCss)}>
            {lastSubmission.officialEvaluation?.status === 'PENDING' && <FontAwesomeIcon icon="history" />}
            {lastSubmission.officialEvaluation?.status !== 'PENDING' && <FontAwesomeIcon icon="spinner" pulse={true} />}
            Last submission
          </button>
          <Modal show={showLastSubmissionModal} onClose={() => setShowLastSubmissionModal(false)}>
            <SubmissionModal data={lastSubmission} />
          </Modal>
          <button className={cx(buttonCss, buttonLightCss)}>
            <FontAwesomeIcon icon="list" />
            All submissions
          </button>
        </>
      )}
    </>
  );
}
