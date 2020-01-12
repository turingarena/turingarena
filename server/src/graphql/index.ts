import { gql } from 'apollo-server-core';
import { querySchema } from './query';
import { mutationSchema } from './mutation';

export const typeDefs = gql`
  ${querySchema}
  ${mutationSchema}
`;

export default typeDefs; // For graphql-codegen
