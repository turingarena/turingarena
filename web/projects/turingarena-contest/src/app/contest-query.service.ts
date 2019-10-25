import { Injectable } from '@angular/core';
import gql from 'graphql-tag';
import { Query } from 'apollo-angular';
import { ContestQuery } from './__generated__/ContestQuery';

@Injectable({
  providedIn: 'root'
})
export class ContestQueryService extends Query<ContestQuery> {
  document = gql`
    query ContestQuery {
      problems {
        name
        material {
          title {
            value
          }
          statement {
            name
            type
            content {
              base64
            }
          }
          attachments {
            title {
              value
            }
            file {
              name
              type
            }
          }
          submissionForm {
            fields {
              id
              title {
                value
              }
              types {
                id
                title {
                  value
                }
                extensions
              }
            }
          }
          feedback {
            __typename
            ... on TableSection {
              caption {
                value
              }
              cols {
                title {
                  value
                }
                content {
                  __typename
                  ... on ScoreColContent {
                    range {
                      precision
                      max
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  `;
}
