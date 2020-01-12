import gql from 'graphql-tag';

export const querySchema = gql`
  type Query {
    a: String!
  }
`;
