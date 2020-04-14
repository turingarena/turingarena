import { gql, useApolloClient } from '@apollo/client';
import { CurrentAuthWriteQuery, CurrentAuthWriteQueryVariables } from '../generated/graphql-types';

export function useAuth() {
  const client = useApolloClient();

  const authQuery = (token: string | null, username: string | null) => {
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
        currentToken: token,
        currentUsername: username,
      },
    });
  };

  const setAuth = ({ token, username }: { token: string; username: string }) => {
    authQuery(token, username);
  };

  const clearAuth = () => {
    authQuery(null, null);
  };

  return { setAuth, clearAuth };
}
