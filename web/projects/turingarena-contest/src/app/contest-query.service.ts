import { Injectable } from '@angular/core';
import gql from 'graphql-tag';
import { Query } from 'apollo-angular';
import { ContestQuery, ContestQueryVariables } from './__generated__/ContestQuery';
import { problemMaterialFragment } from './problem-material';

@Injectable({
  providedIn: 'root'
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
          canSubmit
          submissions {
            id
            status
            createdAt
          }
          scores {
            awardName
            score
          }
          badges {
            awardName
            badge
          }
          ...ProblemMaterialFragment
        }
      }
    }
    ${problemMaterialFragment}
  `;
}
