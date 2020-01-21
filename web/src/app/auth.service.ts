import { Injectable } from '@angular/core';
import { Apollo } from 'apollo-angular';
import gql from 'graphql-tag';

export interface Auth {
  token: string;
  userId: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(private readonly apollo: Apollo) {}

  getAuth() {
    return this.apollo.getClient().readQuery({ query });
  }

  async setAuth(data: Auth | undefined) {
    const client = this.apollo.getClient();
    client.stop();
    await client.resetStore();
    client.writeQuery({ query, data });
    await client.reFetchObservableQueries();
  }
}

const query = gql`
  query Auth {
    userId
    token
  }
`;
