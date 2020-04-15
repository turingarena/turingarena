import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React, { useState } from 'react';
import { ContestProblemAssignmentUserTacklingAsideFragment } from '../generated/graphql-types';
import { buttonBlockCss, buttonCss, buttonOutlineDarkCss, buttonSuccessCss } from '../util/components/button';
import { Modal } from '../util/components/modal';
import { FragmentProps } from '../util/fragment-props';
import {
  ContestProblemAssignmentUserTacklingSubmissionListModal,
  contestProblemAssignmentUserTacklingSubmissionListModalFragment,
} from './contest-problem-assignment-user-tackling-submission-list-modal';
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
  // TODO: change all state to use routing instead
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showLastSubmissionModal, setShowLastSubmissionModal] = useState(false);
  const [showSubmissionListModal, setShowSubmissionListModal] = useState(false);

  const lastSubmission = data.submissions.length > 0 ? data.submissions[data.submissions.length - 1] : null;

  return (
    <div
      className={css`
        display: block;
        padding: 16px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      `}
    >
      {data.canSubmit && (
        <>
          <button onClick={() => setShowSubmitModal(true)} className={cx(buttonCss, buttonBlockCss, buttonSuccessCss)}>
            <FontAwesomeIcon icon="paper-plane" /> Submit a solution
          </button>
          <Modal show={showSubmitModal} onClose={() => setShowSubmitModal(false)}>
            <ContestProblemAssignmentUserTacklingSubmitModal
              data={data}
              onSubmitSuccessful={() => setShowSubmitModal(false)}
            />
          </Modal>
        </>
      )}

      {lastSubmission !== null && (
        <>
          <button
            onClick={() => setShowLastSubmissionModal(true)}
            className={cx(
              buttonCss,
              buttonBlockCss,
              buttonOutlineDarkCss,
              css`
                margin-top: 0.5rem !important; /* FIXME: Bootstrap messes up */
              `,
            )}
          >
            {lastSubmission.officialEvaluation?.status !== 'PENDING' && <FontAwesomeIcon icon="history" />}
            {lastSubmission.officialEvaluation?.status === 'PENDING' && (
              <FontAwesomeIcon icon="spinner" pulse={true} />
            )}{' '}
            Last submission
          </button>

          <Modal show={showLastSubmissionModal} onClose={() => setShowLastSubmissionModal(false)}>
            <SubmissionModal data={lastSubmission} />
          </Modal>

          <button
            onClick={() => setShowSubmissionListModal(true)}
            className={cx(
              buttonCss,
              buttonBlockCss,
              buttonOutlineDarkCss,
              css`
                margin-top: 0.5rem !important; /* FIXME: Bootstrap messes up */
              `,
            )}
          >
            <FontAwesomeIcon icon="list" /> All submissions
          </button>

          <Modal show={showSubmissionListModal} onClose={() => setShowSubmissionListModal(false)}>
            <ContestProblemAssignmentUserTacklingSubmissionListModal data={data} />
          </Modal>
        </>
      )}
    </div>
  );
}
