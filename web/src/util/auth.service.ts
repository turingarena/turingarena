import { Injectable } from '@angular/core';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';
import { AuthQuery, AuthQueryVariables } from '../generated/graphql-types';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(private readonly apollo: Apollo) {}

  getAuth() {
    return this.apollo.getClient().readQuery<AuthQuery, AuthQueryVariables>({ query });
  }

  async setAuth(data: AuthQuery) {
    const client = this.apollo.getClient();
    client.stop();
    await client.resetStore();
    client.writeQuery<AuthQuery, AuthQueryVariables>({ query, data });
    await client.reFetchObservableQueries();
  }
}

const query = gql`
  query Auth {
    userId
    token
  }
`;
