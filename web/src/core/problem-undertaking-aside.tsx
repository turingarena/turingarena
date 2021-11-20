import { gql } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React from 'react';
import { Modal } from 'react-bootstrap';
import { FormattedMessage } from 'react-intl';
import { Link, Route, useHistory, useRouteMatch } from 'react-router-dom';
import { ProblemUndertakingAsideFragment } from '../generated/graphql-types';
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
            <FontAwesomeIcon icon="paper-plane" />{' '}
            <FormattedMessage id="submit-start-button-label" defaultMessage="Submit a solution" />
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
            <FormattedMessage id="last-submission-button-label" defaultMessage="Last submission" />
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
            <FontAwesomeIcon icon="list" />{' '}
            <FormattedMessage id="submission-list-button-label" defaultMessage="All submissions" />
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
                    <FormattedMessage
                      id="submission-list-modal-header"
                      defaultMessage="All submissions for {title}"
                      values={{
                        title: <strong>{data.view.instance.definition.title.variant}</strong>,
                      }}
                    />
                  </h4>
                </Modal.Header>
                <Modal.Body style={{ padding: 0 }}>
                  <ProblemUndertakingSubmissionList data={data} />
                </Modal.Body>
                <Modal.Footer>
                  <button onClick={() => history.replace(path)} className={cx(buttonCss, buttonPrimaryCss)}>
                    <FormattedMessage id="submission-list-modal-close-button-label" defaultMessage="Close" />
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
                  <FormattedMessage
                    id="submission-modal-header"
                    defaultMessage="Submission for {title}"
                    values={{
                      title: <strong>{data.view.instance.definition.title.variant}</strong>,
                    }}
                  />
                </h5>
              </Modal.Header>
              <Modal.Body style={{ padding: 0 }}>
                <SubmissionLoader id={(match.params as { id: string }).id} />
              </Modal.Body>
              <Modal.Footer>
                <button onClick={() => history.replace(path)} className={cx(buttonCss, buttonPrimaryCss)}>
                  <FormattedMessage id="submission-modal-close-button-label" defaultMessage="Close" />
                </button>
              </Modal.Footer>
            </Modal>
          )
        }
      </Route>
    </div>
  );
}
