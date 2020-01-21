import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestView } from './contest-view';
import { User } from './user';

export const mainViewSchema = gql`
    type MainView {
        user: User
        contestView: ContestView
    }
`;

export interface MainView {
    user: User | null;
}

export const mainViewResolvers: ResolversWithModels<{
    MainView: MainView;
}> = {
    MainView: {
        user: ({ user }) => user,
        contestView: async ({ user }, {}, ctx): Promise<ContestView | null> => {
            const contest = await ctx.table(Contest).findOne({ where: { name: 'default' } });
            if (contest === null) return null;

            return { user, contest };
        },
    },
};
