import { gql, useMutation } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import React, { useState } from 'react';
import { LoginMutation, LoginMutationVariables } from '../generated/graphql-types';
import { Modal } from '../util/components/modal';

export function LoginModal({ show, onClose }: { show: boolean; onClose: () => void }) {
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
    <Modal show={show} onClose={onClose}>
      <form
        onSubmit={handleSubmit}
        className={css`
          display: flex;
          flex: 1;
          flex-direction: column;
          margin: 5px;
        `}
      >
        <div
          className={css`
            display: flex;
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
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className={css`
                position: absolute;
                right: 0;
                top: 1px;
              `}
            >
              <FontAwesomeIcon icon="eye" />
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
              <small>Insert the token or password provided to you. No username needed.</small>
            )}
            {!loading && invalidToken && error === undefined && <small>Invalid token.</small>}
          </div>
        </div>
        <div
          className={css`
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
    </Modal>
  );
}
