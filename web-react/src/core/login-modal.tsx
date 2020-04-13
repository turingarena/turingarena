import { gql, useMutation } from '@apollo/client';
import React, { useState } from 'react';
import { LoginMutation } from '../generated/graphql-types';

export function LoginModal() {
  const [invalidToken, setInvalidToken] = useState(false);
  const [token, setToken] = useState('');
  const [logIn] = useMutation<LoginMutation>(gql`
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

  const handleClose = () => {};

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

    handleClose();
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="token">Token</label>
        <input
          className="login-token-input"
          id="token"
          name="token"
          type="password"
          value={token}
          onChange={e => {
            setToken(e.target.value);
          }}
        />
        <small className="login-token-suggestion" hidden={invalidToken}>
          Insert the token or password provided to you. No username needed.
        </small>
        <small className="login-token-invalid" hidden={!invalidToken}>
          Invalid token.
        </small>
      </div>
      <div className="login-dialog-footer">
        <button className="login-dialog-cancel" type="button" onClick={handleClose}>
          Cancel
        </button>
        <button className="login-dialog-submit" type="submit">
          Log in
        </button>
      </div>
    </form>
  );
}
