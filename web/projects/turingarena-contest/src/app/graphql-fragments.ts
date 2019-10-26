import gql from 'graphql-tag';
export const problemMaterialFragment = gql`
  fragment ProblemMaterialFragment on Problem {
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
`;
