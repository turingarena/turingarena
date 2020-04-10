import { Injectable } from '@angular/core';
import { Apollo } from 'apollo-angular';
import { currentAuthQuery } from '../config/graphql.module';
import { AuthResult, CurrentAuthQuery } from '../generated/graphql-types';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(private readonly apollo: Apollo) {}

  async removeAuth() {
    await this.apollo.getClient().clearStore();
    this.apollo.getClient().writeQuery<CurrentAuthQuery>({
      query: currentAuthQuery,
      data: {
        __typename: 'Query',
        currentAuth: null,
      },
    });
  }

  async setAuth(currentAuth: AuthResult) {
    await this.removeAuth();
    this.apollo.getClient().writeQuery<CurrentAuthQuery>({
      query: currentAuthQuery,
      data: {
        __typename: 'Query',
        currentAuth,
      },
    });
  }
}
