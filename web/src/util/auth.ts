import { gql, InMemoryCache, useApolloClient, useQuery } from '@apollo/client';
import { CurrentAuthQuery, CurrentAuthQueryVariables } from '../generated/graphql-types';

export interface AuthData {
  token: string;
  username: string;
}

export const currentAuthQuery = gql`
  query CurrentAuth {
    currentAuth @client {
      token
      username
    }
  }
`;

export function initAuthCache(cache: InMemoryCache) {
  cache.writeQuery<CurrentAuthQuery, CurrentAuthQueryVariables>({
    query: currentAuthQuery,
    data: {
      __typename: 'Query',
      currentAuth: null,
    },
  });
}

export function readAuthCache(cache: InMemoryCache) {
  return cache.readQuery<CurrentAuthQuery, CurrentAuthQueryVariables>({
    query: currentAuthQuery,
  });
}

export function useAuth() {
  const client = useApolloClient();

  const { data: auth } = useQuery<CurrentAuthQuery, CurrentAuthQueryVariables>(currentAuthQuery);

  const setAuth = ({ token, username }: AuthData) => {
    client.writeQuery<CurrentAuthQuery, CurrentAuthQueryVariables>({
      query: currentAuthQuery,
      data: {
        __typename: 'Query',
        currentAuth: {
          __typename: 'CurrentAuth' as const,
          token,
          username,
        },
      },
    });

    localStorage.setItem('auth', JSON.stringify({ token, username }));
  };

  const clearAuth = () => {
    // FIXME: breaks AgGrid
    // await client.resetStore();

    client.writeQuery<CurrentAuthQuery, CurrentAuthQueryVariables>({
      query: currentAuthQuery,
      data: {
        __typename: 'Query',
        currentAuth: null,
      },
    });

    localStorage.removeItem('auth');
  };

  const restoreAuth = () => {
    const authJson = localStorage.getItem('auth');

    if (authJson !== null) {
      try {
        const { token, username } = JSON.parse(authJson) as AuthData;
        setAuth({ token, username });

        return;
      } catch {}
    }

    clearAuth();
  };

  return { auth, setAuth, clearAuth, restoreAuth };
}

export function bearerHeader(){
  const authJson = localStorage.getItem('auth');

    if (authJson !== null) {
      try {
        const { token, username } = JSON.parse(authJson);
        
        return{Authorization: `Bearer ${token}`};
      } catch {
        return {};
      }
    }
    return {};
}