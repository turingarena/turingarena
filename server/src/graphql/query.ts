import { gql } from 'apollo-server-core';

export const querySchema = gql`
  type Query {
    a: String!
  }
`;
