import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React from 'react';
import { Modal } from 'react-bootstrap';
import { Link, Route, useHistory, useRouteMatch } from 'react-router-dom';
import { ProblemUndertakingAsideFragment } from '../generated/graphql-types';
import { useT } from '../translations/main';
import {
  buttonBlockCss,
  buttonCss,
  buttonOutlineDarkCss,
  buttonPrimaryCss,
  buttonSuccessCss,
} from '../util/components/button';
import { FragmentProps } from '../util/fragment-props';
import {
  ProblemUndertakingSubmissionList,
  problemUndertakingSubmissionListFragment,
} from './problem-undertaking-submission-list';
import {
  ProblemUndertakingSubmitModal,
  problemUndertakingSubmitModalFragment,
} from './problem-undertaking-submit-modal';
import { SubmissionLoader } from './submission-loader';

export const problemUndertakingAsideFragment = gql`
  fragment ProblemUndertakingAside on ProblemUndertaking {
    canSubmit
    submissions {
      id
      officialEvaluation {
        id
      }
    }

    ...ProblemUndertakingSubmitModal
    ...ProblemUndertakingSubmissionList
  }

  ${problemUndertakingSubmitModalFragment}
  ${problemUndertakingSubmissionListFragment}
`;

export function ProblemUndertakingAside({ data }: FragmentProps<ProblemUndertakingAsideFragment>) {
  const routeMatch = useRouteMatch();
  const path = routeMatch?.path;
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
          <Link className={cx(buttonCss, buttonBlockCss, buttonSuccessCss)} to={`${path}/submit`} replace>
            <FontAwesomeIcon icon="paper-plane" /> {t('submitASolution')}
          </Link>
          <Route path={`${path}/submit`}>
            {({ match }) => (
              <Modal show={match !== null} onHide={() => history.replace(path)}>
                <ProblemUndertakingSubmitModal
                  data={data}
                  onSubmitSuccessful={id => history.replace(`${path}/submission/${id}`)}
                />
              </Modal>
            )}
          </Route>
        </>
      )}

      {lastSubmission !== null && (
        <>
          <Link
            to={`${path}/submission/${lastSubmission.id}`}
            className={cx(
              buttonCss,
              buttonBlockCss,
              buttonOutlineDarkCss,
              css`
                margin-top: 0.5rem !important; /* FIXME: Bootstrap messes up */
              `,
            )}
          >
            {lastSubmission.officialEvaluation !== null && <FontAwesomeIcon icon="history" />}
            {lastSubmission.officialEvaluation === null && <FontAwesomeIcon icon="spinner" pulse={true} />}{' '}
            {t('lastSubmission')}
          </Link>

          <Link
            to={`${path}/submissions`}
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
          <Route path={`${path}/submissions`}>
            {({ match }) => (
              <Modal
                show={match !== null}
                onHide={() => history.replace(path)}
                animation={false}
                size="xl"
                scrollable={true}
              >
                <Modal.Header>
                  <h4>
                    {t('submissionsFor')}: <strong>{data.view.instance.definition.title.variant}</strong>
                  </h4>
                </Modal.Header>
                <Modal.Body style={{ padding: 0 }}>
                  <ProblemUndertakingSubmissionList data={data} />
                </Modal.Body>
                <Modal.Footer>
                  <button onClick={() => history.replace(path)} className={cx(buttonCss, buttonPrimaryCss)}>
                    Close
                  </button>
                </Modal.Footer>
              </Modal>
            )}
          </Route>
        </>
      )}
      <Route path={`${path}/submission/:id`}>
        {({ match }) =>
          match !== null && (
            <Modal onHide={() => history.replace(path)} show={true} animation={false} size="xl" scrollable={true}>
              <Modal.Header>
                <h5>
                  {/* TODO: submission index, e.g., Submission #6 for: My Problem */}
                  {t('submissionsFor')}: <strong>{data.view.instance.definition.title.variant}</strong>
                </h5>
              </Modal.Header>
              <Modal.Body style={{ padding: 0 }}>
                <SubmissionLoader id={(match.params as { id: string }).id} />
              </Modal.Body>
              <Modal.Footer>
                <button onClick={() => history.replace(path)} className={cx(buttonCss, buttonPrimaryCss)}>
                  {t('close')}
                </button>
              </Modal.Footer>
            </Modal>
          )
        }
      </Route>
    </div>
  );
}
