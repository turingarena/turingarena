import { Resolvers } from './__generated__/graphql';
import { User } from './db';

export const resolvers: Resolvers = {
  Query: {
    a: async () => {
      await User.sync();
      await User.create({
        nickname: 'a string',
      });

      const user = await User.findOne();

      return user!.nickname;
    },
  },
  Mutation: {
    b: () => 'another string',
  },
};
