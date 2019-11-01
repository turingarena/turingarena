import { Injectable } from '@angular/core';
import { Query } from 'apollo-angular';
import gql from 'graphql-tag';

import { SubmissionListQuery, SubmissionListQueryVariables } from './__generated__/SubmissionListQuery';
import { problemMaterialFragment } from './problem-material';
import { submissionFragment } from './submission';
import { problemFragment } from './problem';

@Injectable({
  providedIn: 'root',
})
export class SubmissionListQueryService extends Query<SubmissionListQuery, SubmissionListQueryVariables> {
  document = gql`
    query SubmissionListQuery($userId: UserId!, $problemName: ProblemName!) {
      contestView(userId: $userId) {
        user {
          id
        }
        problem(name: $problemName) {
          ...ProblemMaterialFragment
          ...ProblemStateFragment
          submissions { ...SubmissionFragment }
        }
      }
    }
    ${problemMaterialFragment}
    ${problemFragment}
    ${submissionFragment}
  `;
}
