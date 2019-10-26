import { Injectable } from '@angular/core';
import { Query } from 'apollo-angular';
import gql from 'graphql-tag';
import { SubmissionQuery, SubmissionQueryVariables } from './__generated__/SubmissionQuery';

@Injectable({
  providedIn: 'root'
})
export class SubmissionQueryService extends Query<SubmissionQuery, SubmissionQueryVariables> {
  document = gql`
    query SubmissionQuery($submissionId: String!) {
      submission(submissionId: $submissionId) {
        evaluationEvents {
          event {
            __typename
            ... on ValueEvent {
              key
              value {
                __typename
                ... on TextValue {
                  text {
                    value
                  }
                }
                ... on ScoreValue {
                  score
                }
              }
            }
          }
        }
      }
    }
  `;
}
