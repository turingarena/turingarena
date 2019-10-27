import gql from 'graphql-tag';

export const textFragment = gql`
  fragment TextFragment on TextVariant {
    attributes {
      key
      value
    }
    value
  }
`;

export const problemMaterialFragment = gql`
  fragment ProblemMaterialFragment on Problem {
    material {
      title {
        ...TextFragment
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
          ...TextFragment
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
            ...TextFragment
          }
          types {
            id
            title {
              ...TextFragment
            }
            extensions
          }
        }
      }
      awards {
        name
        title {
          ...TextFragment
        }
        content {
          __typename
          ... on ScoreAwardContent {
            range {
              precision
              max
            }
          }
        }
      }
      feedback {
        __typename
        ... on TableSection {
          caption {
            ...TextFragment
          }
          cols {
            title {
              ...TextFragment
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
              ...TextFragment
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
                      ...TextFragment
                    }
                  }
                  ... on ScoreCellContent {
                    ref
                    range {
                      max
                      precision
                    }
                  }
                  ... on MessageCellContent {
                    ref
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  ${textFragment}
`;
