import gql from 'graphql-tag';

export const mutationSchema = gql`
  type Mutation {
    b: String!
  }
`;
