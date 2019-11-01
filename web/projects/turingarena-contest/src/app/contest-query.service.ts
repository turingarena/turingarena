import { Injectable } from '@angular/core';
import { Query } from 'apollo-angular';
import gql from 'graphql-tag';

import { ContestQuery, ContestQueryVariables } from './__generated__/ContestQuery';
import { problemMaterialFragment } from './problem-material';
import { problemFragment } from './problem';
import { submissionFragment } from './submission';

@Injectable({
  providedIn: 'root',
})
export class ContestQueryService extends Query<ContestQuery, ContestQueryVariables> {
  document = gql`
    query ContestQuery($userId: UserId) {
      serverTime
      contestView(userId: $userId) {
        user {
          id
          displayName
        }
        contestTitle
        startTime
        endTime
        problems {
          name
          tackling {
            ...ProblemTacklingFragment
            submissions { ...SubmissionFragment }
          }
          ...ProblemMaterialFragment
        }
      }
    }
    ${problemFragment}
    ${problemMaterialFragment}
    ${submissionFragment}
  `;
}
