import { gql } from 'apollo-server-core';

export const querySchema = gql`
  type Query {
    value: String!
  }
`;
