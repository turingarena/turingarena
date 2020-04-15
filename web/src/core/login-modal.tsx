import { gql, useMutation } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React, { useState } from 'react';
import { LoginMutation, LoginMutationVariables } from '../generated/graphql-types';
import { useAsync } from '../util/async-hook';
import { useAuth } from '../util/auth';
import { buttonCss, buttonOutlineSecondaryCss, buttonPrimaryCss, buttonSecondaryCss } from '../util/components/button';
import {
  formControlCss,
  formTextCss,
  inputGroupAppendCss,
  inputGroupCss,
  invalidCss,
  invalidFeedbackCss,
} from '../util/components/form';
import { modalBodyCss, modalFooterCss } from '../util/components/modal';

class InvalidTokenError extends Error {}

export function LoginModal({ onClose }: { onClose: () => void }) {
  const [showPassword, setShowPassword] = useState(false);
  const auth = useAuth();
  const [token, setToken] = useState('');

  const [logInMutate] = useMutation<LoginMutation, LoginMutationVariables>(gql`
    mutation Login($token: String!) {
      logIn(token: $token) {
        user {
          id
          name
          username
        }
        token
      }
    }
  `);

  const [logIn, { loading, error, successful }] = useAsync(async () => {
    const { data } = await logInMutate({
      variables: {
        token,
      },
      fetchPolicy: 'no-cache',
    });

    if (data === null || data === undefined) {
      throw new Error('error during login');
    }

    if (data.logIn === null) {
      throw new InvalidTokenError('invalid token');
    }

    auth.setAuth({
      username: data.logIn?.user.username,
      token: data.logIn?.token,
    });

    onClose();
  });

  return (
    <form
      onSubmit={e => {
        e.preventDefault();
        logIn();
      }}
      className={css`
        display: flex;
        flex: 1;
        flex-direction: column;
        align-items: space-between;
        width: 28rem;
      `}
    >
      <div
        className={css`
          display: flex;
          flex: 1;
          flex-direction: column;
        `}
      >
        <div className={cx(modalBodyCss)}>
          <label htmlFor="token">Token</label>
          <div className={cx(inputGroupCss, error instanceof InvalidTokenError ? [invalidCss] : undefined)}>
            <input
              type={showPassword ? 'text' : 'password'}
              value={token}
              autoFocus
              onChange={e => setToken(e.target.value)}
              className={cx(formControlCss, error instanceof InvalidTokenError ? [invalidCss] : undefined)}
            />
            <div className={inputGroupAppendCss}>
              <button
                onClick={e => {
                  setShowPassword(!showPassword);
                  e.preventDefault();
                }}
                type="button"
                className={cx(
                  buttonCss,
                  buttonOutlineSecondaryCss,
                  css`
                    cursor: pointer;
                  `,
                )}
              >
                <FontAwesomeIcon
                  icon={showPassword ? 'eye-slash' : 'eye'}
                  style={{ width: '20px' }} // HACK: 20 is the max between the widths of the two icons
                />
              </button>
            </div>
          </div>
          {loading ? (
            <small className={cx(formTextCss)}>Logging in...</small>
          ) : error instanceof InvalidTokenError ? (
            <small className={cx(invalidFeedbackCss)}>Invalid token, please try again.</small>
          ) : error !== undefined ? (
            <small className={cx(invalidFeedbackCss)}>{error.message}</small>
          ) : successful ? (
            <small className={cx(formTextCss)}>Logged in!</small>
          ) : (
            <small className={cx(formTextCss)}>Insert the token or password provided to you. No username needed.</small>
          )}
        </div>
      </div>
      <div className={modalFooterCss}>
        <button
          className={cx(
            buttonCss,
            buttonSecondaryCss,
            css`
              margin-right: 3px;
            `,
          )}
          onClick={e => {
            e.preventDefault();
            onClose();
          }}
          disabled={loading}
          type="button"
        >
          Cancel
        </button>
        <button className={cx(buttonCss, buttonPrimaryCss)} disabled={loading} type="submit">
          Log in
        </button>
      </div>
    </form>
  );
}
