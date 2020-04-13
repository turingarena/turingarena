import { gql, useMutation } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css } from 'emotion';
import React, { useState } from 'react';
import { LoginMutation, LoginMutationVariables } from '../generated/graphql-types';
import { Button } from '../util/components/button';
import { PasswordInput } from '../util/components/password-input';

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

  const handleLogIn = async () => {
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
      onSubmit={e => e.preventDefault()}
      className={css`
        display: flex;
        width: 300px;
        height: 130px;
        flex: 1;
        flex-direction: column;
        align-items: space-between;
        margin: 5px;
      `}
    >
      <div
        className={css`
          display: flex;
          flex: 1;
          flex-direction: column;
          margin-left: 5px;
          margin-right: 5px;
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
        <PasswordInput password={token} onChange={setToken} />
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
        <Button
          onPress={onClose}
          disabled={loading}
          title="Cancel"
          className={css`
            margin-right: 3px;
          `}
        />
        <Button onPress={handleLogIn} disabled={loading} title="Log In" primary />
      </div>
    </form>
  );
}
