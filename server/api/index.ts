import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';
import { mutationResolvers, mutationSchema } from './mutation';
import { queryResolvers, querySchema } from './query';
import { userSchema } from './user';

export const schema = gql`
  ${querySchema}
  ${mutationSchema}
  ${userSchema}
`;

export const resolvers: Resolvers = {
  ...queryResolvers,
  ...mutationResolvers,
};

// tslint:disable-next-line: no-default-export
export default schema; // For graphql-codegen
