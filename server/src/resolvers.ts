import { Resolvers } from './__generated__/graphql';

export const resolvers: Resolvers = {
  Query: {
    a: () => 'a string',
  },
  Mutation: {
    b: () => 'another string',
  },
};
