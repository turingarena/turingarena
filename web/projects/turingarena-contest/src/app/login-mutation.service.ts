import { Injectable } from '@angular/core';
import { Mutation } from 'apollo-angular';
import gql from 'graphql-tag';
import { LoginMutation, LoginMutationVariables } from './__generated__/LoginMutation';

@Injectable({
  providedIn: 'root'
})
export class LoginMutationService extends Mutation<LoginMutation, LoginMutationVariables> {
  document = gql`
    mutation LoginMutation($token: String!) {
      auth(token: $token) {
        token
      }
    }
  `;
}
