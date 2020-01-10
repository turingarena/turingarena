import gql from 'graphql-tag';

export const messageFragment = gql`
  fragment MessageFragment on Message {
    id
    createdAt
    kind
    text
    problem {
      name
    }
  }
`;
