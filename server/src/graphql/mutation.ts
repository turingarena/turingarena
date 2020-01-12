import { gql } from 'apollo-server-core';

export const mutationSchema = gql`
  type Mutation {
    b: String!
  }
`;
