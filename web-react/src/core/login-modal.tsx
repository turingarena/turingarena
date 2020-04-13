import { gql, useApolloClient, useMutation } from '@apollo/client';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { css, cx } from 'emotion';
import React, { useState } from 'react';
import {
  CurrentAuthWriteQuery,
  CurrentAuthWriteQueryVariables,
  LoginMutation,
  LoginMutationVariables,
} from '../generated/graphql-types';
import { buttonCss, buttonLightCss, buttonNormalizeCss, buttonPrimaryCss } from '../util/components/button';

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

  const client = useApolloClient();

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

    // FIXME: breaks AgGrid
    // await client.resetStore();
    client.writeQuery<CurrentAuthWriteQuery, CurrentAuthWriteQueryVariables>({
      query: gql`
        query CurrentAuthWrite {
          currentToken @client
          currentUsername @client
        }
      `,
      data: {
        __typename: 'Query',
        currentToken: data.logIn?.token,
        currentUsername: data.logIn?.user.username,
      },
    });

    onClose();
  };

  return (
    <form
      action=""
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
            onClick={() => setShowPassword(!showPassword)}
            className={cx(
              buttonNormalizeCss,
              css`
                position: absolute;
                right: 5px;
                bottom: 5px;
                cursor: pointer;
              `,
            )}
          >
            <FontAwesomeIcon icon={showPassword ? 'eye-slash' : 'eye'} />
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
            buttonLightCss,
            css`
              margin-right: 3px;
            `,
          )}
          onClick={onClose}
          disabled={loading}
          type="button"
        >
          Cancel
        </button>
        <button className={cx(buttonCss, buttonPrimaryCss)} onClick={handleLogIn} disabled={loading} type="submit">
          Log In
        </button>
      </div>
    </form>
  );
}
