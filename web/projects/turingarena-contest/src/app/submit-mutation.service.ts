import { Injectable } from '@angular/core';
import { Mutation } from 'apollo-angular';
import gql from 'graphql-tag';

import { SubmitMutation, SubmitMutationVariables } from './__generated__/SubmitMutation';

@Injectable({
  providedIn: 'root',
})
export class SubmitMutationService extends Mutation<SubmitMutation, SubmitMutationVariables> {
  document = gql`
    mutation SubmitMutation($userId: UserId!, $problemName: ProblemName!, $files: [FileInput!]!) {
      contestView(userId: $userId) {
        problem(name: $problemName) {
          tackling {
            submit(files: $files) {
              id
            }
          }
        }
      }
    }
  `;
}
