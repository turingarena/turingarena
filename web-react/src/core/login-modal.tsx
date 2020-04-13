import { gql, useMutation } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import React, { useState } from 'react';
import { LoginMutation, LoginMutationVariables } from '../generated/graphql-types';

export function LoginModal({ onClose }: { onClose: () => void }) {
  const [invalidToken, setInvalidToken] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [token, setToken] = useState('');
  const [logIn, { loading, error }] = useMutation<LoginMutation, LoginMutationVariables>(gql`
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

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const { data } = await logIn({
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

    // await this.authService.setAuth(data.logIn);

    onClose();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={css`
        display: flex;
        width: 300px;
        height: 130px;
        flex: 1;
        flex-direction: column;
        align-items: space-between;
        margin: 10px;
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
            id="token"
            name="token"
            type={showPassword ? 'text' : 'password'}
            value={token}
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
          <a
            onClick={() => setShowPassword(!showPassword)}
            className={css`
              position: absolute;
              right: 5px;
              bottom: 5px;
            `}
          >
            <FontAwesomeIcon icon="eye" color={!showPassword ? '#000000' : '#707070'} />
          </a>
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
          margin-top: 15px;
          align-self: flex-end;
        `}
      >
        <button className="login-dialog-cancel" type="button" onClick={onClose} disabled={loading}>
          Cancel
        </button>
        <button className="login-dialog-submit" type="submit" disabled={loading}>
          Log in
        </button>
      </div>
    </form>
  );
}
