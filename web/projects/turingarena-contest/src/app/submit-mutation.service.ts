import { Injectable } from '@angular/core';
import { Mutation } from 'apollo-angular';
import gql from 'graphql-tag';
import { SubmitMutation, SubmitMutationVariables } from './__generated__/SubmitMutation';

@Injectable({
  providedIn: 'root'
})
export class SubmitMutationService extends Mutation<SubmitMutation, SubmitMutationVariables> {
  document = gql`
    mutation SubmitMutation($userId: String!, $problemName: String!, $files: [FileInput!]!) {
      submit(userId: $userId, problemName: $problemName, files: $files) {
        id
      }
    }
  `;
}
