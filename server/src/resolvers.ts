import { Resolvers } from './__generated__/graphql';
import { mutationResolvers } from './mutation/resolvers';
import { queryResolvers } from './query/resolvers';

export const resolvers: Resolvers = {
  ...queryResolvers,
  ...mutationResolvers,
};
