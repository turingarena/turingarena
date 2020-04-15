import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React from 'react';
import { Link, Route, useHistory } from 'react-router-dom';
import { ContestProblemAssignmentUserTacklingAsideFragment } from '../generated/graphql-types';
import {
  buttonBlockCss,
  buttonCss,
  buttonOutlineDarkCss,
  buttonPrimaryCss,
  buttonSuccessCss,
} from '../util/components/button';
import { gridCss } from '../util/components/grid';
import { Modal, modalFooterCss, modalHeaderCss } from '../util/components/modal';
import { FragmentProps } from '../util/fragment-props';
import { SetBasePath, useBasePath } from '../util/paths';
import {
  ContestProblemAssignmentUserTacklingSubmissionList,
  contestProblemAssignmentUserTacklingSubmissionListFragment,
} from './contest-problem-assignment-user-tackling-submission-list';
import {
  ContestProblemAssignmentUserTacklingSubmitModal,
  contestProblemAssignmentUserTacklingSubmitModalFragment,
} from './contest-problem-assignment-user-tackling-submit-modal';
import { SubmissionLoader } from './submission-loader';

export const contestProblemAssignmentUserTacklingAsideFragment = gql`
  fragment ContestProblemAssignmentUserTacklingAside on ContestProblemAssignmentUserTackling {
    canSubmit
    submissions {
      id
      officialEvaluation {
        status
      }
    }

    ...ContestProblemAssignmentUserTacklingSubmitModal
    ...ContestProblemAssignmentUserTacklingSubmissionList
  }

  ${contestProblemAssignmentUserTacklingSubmitModalFragment}
  ${contestProblemAssignmentUserTacklingSubmissionListFragment}
`;

export function ContestProblemAssignmentUserTacklingAside({
  data,
}: FragmentProps<ContestProblemAssignmentUserTacklingAsideFragment>) {
  const basePath = useBasePath();
  const history = useHistory();

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
          <Link className={cx(buttonCss, buttonBlockCss, buttonSuccessCss)} to={`${basePath}/submit`} replace>
            <FontAwesomeIcon icon="paper-plane" /> Submit a solution
          </Link>
          <Route path={`${basePath}/submit`}>
            {({ match }) => (
              <Modal show={match !== null} onClose={() => history.replace(basePath)}>
                <ContestProblemAssignmentUserTacklingSubmitModal
                  data={data}
                  onSubmitSuccessful={() => history.goBack()}
                />
              </Modal>
            )}
          </Route>
        </>
      )}

      {lastSubmission !== null && (
        <>
          <Link
            to={`${basePath}/submission/${lastSubmission.id}`}
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
          </Link>

          <Link
            to={`${basePath}/submissions`}
            replace
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
          </Link>
          <Route path={`${basePath}/submissions`}>
            {({ match }) => (
              <Modal show={match !== null} onClose={() => history.replace(basePath)}>
                <div className={modalHeaderCss}>
                  <h4>
                    Submissions for: <strong>{data.assignmentView.assignment.problem.title.variant}</strong>
                  </h4>
                </div>
                <div
                  className={cx(
                    gridCss,
                    css`
                      padding: 0;
                      max-height: calc(100vh - 260px);
                      overflow-y: auto;
                      width: 80vw;
                    `,
                  )}
                >
                  <ContestProblemAssignmentUserTacklingSubmissionList data={data} />
                </div>
                <div className={modalFooterCss}>
                  <button onClick={() => history.replace(basePath)} className={cx(buttonCss, buttonPrimaryCss)}>
                    Close
                  </button>
                </div>
              </Modal>
            )}
          </Route>
        </>
      )}
      <Route path={`${basePath}/submission/:id`}>
        {({ match }) =>
          match !== null && (
            <SetBasePath path={`${basePath}/submission/${(match.params as { id: string }).id}`}>
              <Modal onClose={() => history.replace(basePath)}>
                <div
                  className={css`
                    width: 80vw;
                    overflow: auto;
                  `}
                >
                  <div className={modalHeaderCss}>
                    <h5>
                      {/* TODO: submission index, e.g., Submission #6 for: My Problem */}
                      Submission for: <strong>{data.assignmentView.assignment.problem.title.variant}</strong>
                    </h5>
                  </div>
                  <SubmissionLoader id={(match.params as { id: string }).id} />
                  <div className={modalFooterCss}>
                    <button onClick={() => history.replace(basePath)} className={cx(buttonCss, buttonPrimaryCss)}>
                      Close
                    </button>
                  </div>
                </div>
              </Modal>
            </SetBasePath>
          )
        }
      </Route>
    </div>
  );
}
