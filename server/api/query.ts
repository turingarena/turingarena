import { gql } from 'apollo-server-core';
import { Resolvers } from '../generated/graphql-types';
import { User } from './user';

export const querySchema = gql`
  type Query {
    users: [User!]!
  }
`;

export const queryResolvers: Resolvers = {
  Query: {
    users: async () => User.findAll(),
    // value: async () => 'a string',
  },
};
