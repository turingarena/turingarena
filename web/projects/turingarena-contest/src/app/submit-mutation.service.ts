import { Injectable } from '@angular/core';
import { Mutation } from 'apollo-angular';
import gql from 'graphql-tag';
import { SubmitMutation, SubmitMutationVariables } from './__generated__/SubmitMutation';

@Injectable({
  providedIn: 'root'
})
export class SubmitMutationService extends Mutation<SubmitMutation, SubmitMutationVariables> {
  document = gql`
    mutation SubmitMutation($userId: String!, $problemName: ProblemName!, $files: [FileInput!]!) {
      user(id: $userId) {
        problem(name: $problemName) {
          submit(files: $files) {
            id
          }
        }
      }
    }
  `;
}
