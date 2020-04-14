import { ApolloClient, gql, useApolloClient } from '@apollo/client';
import { CurrentAuthWriteQuery, CurrentAuthWriteQueryVariables } from '../generated/graphql-types';

const authQuery = gql`
  query CurrentAuthWrite {
    currentToken @client
    currentUsername @client
  }
`;

class Auth {
  constructor(private readonly client: ApolloClient<object>) {}

  private authQuery(token: string | null, username: string | null) {
    // FIXME: breaks AgGrid
    // await client.resetStore();
    this.client.writeQuery<CurrentAuthWriteQuery, CurrentAuthWriteQueryVariables>({
      query: authQuery,
      data: {
        __typename: 'Query',
        currentToken: token,
        currentUsername: username,
      },
    });
  }

  setAuth({ token, username }: { token: string; username: string }) {
    this.authQuery(token, username);
  }

  clearAuth() {
    this.authQuery(null, null);
  }
}

export function useAuth() {
  const client = useApolloClient();

  return new Auth(client);
}
