import { Injectable } from '@angular/core';
import gql from 'graphql-tag';
import { Query } from 'apollo-angular';
import { ContestQuery, ContestQueryVariables } from './__generated__/ContestQuery';

@Injectable({
  providedIn: 'root'
})
export class ContestQueryService extends Query<ContestQuery, ContestQueryVariables> {
  document = gql`
    query ContestQuery($userId: String!) {
      user(id: $userId) {
        displayName
      }
      config {
        contestTitle
        startTime
        endTime
      }
      problems {
        name
        submissions(userId: $userId) {
          createdAt
        }
        scorables(userId: $userId) {
          scorableId
          score
        }
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
              content {
                base64
              }
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
          scorables {
            name
            title {
              value
            }
            range {
              precision
              max
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
              rowGroups {
                title {
                  value
                }
                rows {
                  content
                  cells {
                    content {
                      __typename
                      ... on RowNumberCellContent {
                        number
                      }
                      ... on RowTitleCellContent {
                        title {
                          value
                        }
                      }
                      ... on ScoreCellContent {
                        ref
                        range {
                          max
                          precision
                        }
                      }
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
