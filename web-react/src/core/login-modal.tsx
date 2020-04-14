import { gql, useMutation } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React, { useState } from 'react';
import { LoginMutation, LoginMutationVariables } from '../generated/graphql-types';
import { useAsync } from '../util/async-hook';
import { useAuth } from '../util/auth';
import { buttonCss, buttonNormalizeCss, buttonPrimaryCss, buttonSecondaryCss } from '../util/components/button';

export function LoginModal({ onClose }: { onClose: () => void }) {
  const [invalidToken, setInvalidToken] = useState(false);
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

  const [logIn, { loading, error }] = useAsync(async () => {
    const { data } = await logInMutate({
      variables: {
        token,
      },
      fetchPolicy: 'no-cache',
    });

    if (data === null || data === undefined) {
      throw Error('error during login');
    }

    if (data.logIn === null) {
      setInvalidToken(true);

      return;
    }

    auth.setAuth({
      username: data.logIn?.user.username,
      token: data.logIn?.token,
    });

    onClose();
  });

  return (
    <form
      onSubmit={async e => {
        e.preventDefault();
        await logIn();
      }}
      className={css`
        display: flex;
        flex: 1;
        flex-direction: column;
        align-items: space-between;
      `}
    >
      <div
        className={css`
          display: flex;
          flex: 1;
          flex-direction: column;
        `}
      >
        <label
          htmlFor="token"
          className={css`
            font-size: 20pt;
          `}
        >
          Token
        </label>
        <div
          className={css`
            position: relative;
            display: inline-block;
          `}
        >
          <input
            type={showPassword ? 'text' : 'password'}
            value={token}
            autoFocus
            onChange={e => setToken(e.target.value)}
            className={css`
              width: 100%;
              border-width: 0 0 2px;
              font-size: 16pt;

              &:focus {
                outline: none;
              }
            `}
          />
          <button
            onClick={e => {
              setShowPassword(!showPassword);
              e.preventDefault();
            }}
            type="button"
            className={cx(
              buttonNormalizeCss,
              css`
                position: absolute;
                right: 5px;
                bottom: 4px;
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
        <div
          className={css`
            margin-top: 1px;
          `}
        >
          {loading && <small>Logging in...</small>}
          {error !== undefined && <small>Cannot login: {error.message}</small>}
          {!loading && !invalidToken && error === undefined && (
            <small>
              Insert the token or password provided to you.
              <br />
              No username needed.
            </small>
          )}
          {!loading && invalidToken && error === undefined && <small>Invalid token.</small>}
        </div>
      </div>
      <div
        className={css`
          align-self: flex-end;
        `}
      >
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
          Log In
        </button>
      </div>
    </form>
  );
}
