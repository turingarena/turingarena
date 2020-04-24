import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React from 'react';
import { Modal } from 'react-bootstrap';
import { Link, Route, useHistory } from 'react-router-dom';
import { ContestProblemAssignmentUserTacklingAsideFragment } from '../generated/graphql-types';
import { useT } from '../translations/main';
import {
  buttonBlockCss,
  buttonCss,
  buttonOutlineDarkCss,
  buttonPrimaryCss,
  buttonSuccessCss,
} from '../util/components/button';
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
  const t = useT();

  const lastSubmission = data.submissions.length > 0 ? data.submissions[0] : null;

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
            <FontAwesomeIcon icon="paper-plane" /> {t('submitASolution')}
          </Link>
          <Route path={`${basePath}/submit`}>
            {({ match }) => (
              <Modal show={match !== null} onHide={() => history.replace(basePath)}>
                <ContestProblemAssignmentUserTacklingSubmitModal
                  data={data}
                  onSubmitSuccessful={id => history.replace(`${basePath}/submission/${id}`)}
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
            {t('lastSubmission')}
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
            <FontAwesomeIcon icon="list" /> {t('allSubmissions')}
          </Link>
          <Route path={`${basePath}/submissions`}>
            {({ match }) => (
              <Modal
                show={match !== null}
                onHide={() => history.replace(basePath)}
                animation={false}
                size="xl"
                scrollable={true}
              >
                <Modal.Header>
                  <h4>
                    {t('submissionsFor')}: <strong>{data.assignmentView.assignment.problem.title.variant}</strong>
                  </h4>
                </Modal.Header>
                <Modal.Body style={{ padding: 0 }}>
                  <ContestProblemAssignmentUserTacklingSubmissionList data={data} />
                </Modal.Body>
                <Modal.Footer>
                  <button onClick={() => history.replace(basePath)} className={cx(buttonCss, buttonPrimaryCss)}>
                    Close
                  </button>
                </Modal.Footer>
              </Modal>
            )}
          </Route>
        </>
      )}
      <Route path={`${basePath}/submission/:id`}>
        {({ match }) =>
          match !== null && (
            <SetBasePath path={`${basePath}/submission/${(match.params as { id: string }).id}`}>
              <Modal onHide={() => history.replace(basePath)} show={true} animation={false} size="xl" scrollable={true}>
                <Modal.Header>
                  <h5>
                    {/* TODO: submission index, e.g., Submission #6 for: My Problem */}
                    {t('submissionsFor')}: <strong>{data.assignmentView.assignment.problem.title.variant}</strong>
                  </h5>
                </Modal.Header>
                <Modal.Body style={{ padding: 0 }}>
                  <SubmissionLoader id={(match.params as { id: string }).id} />
                </Modal.Body>
                <Modal.Footer>
                  <button onClick={() => history.replace(basePath)} className={cx(buttonCss, buttonPrimaryCss)}>
                    {t('close')}
                  </button>
                </Modal.Footer>
              </Modal>
            </SetBasePath>
          )
        }
      </Route>
    </div>
  );
}
