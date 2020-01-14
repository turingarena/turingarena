import { gql } from 'apollo-server-core';
import { sequelize } from '../db';
import { Resolvers } from '../generated/graphql-types';

export const mutationSchema = gql`
  type Mutation {
    init: Query!
  }
`;

export const mutationResolvers: Resolvers = {
  Mutation: {
    init: async () => {
      await sequelize.sync();

      return {};
    },
  },
};
