import { gql } from 'apollo-server-core';
import { ApiContext } from '../main/context';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestView } from './contest-view';
import { Text } from './material/text';
import { User } from './user';

export const mainViewSchema = gql`
    type MainView {
        user: User
        title: Text!
        contestView: ContestView
    }
`;

export class MainView {
    constructor(readonly user: User | null) {}

    async getContest(ctx: ApiContext) {
        return ctx.table(Contest).findOne({ where: { name: 'default' } });
    }
}

export const mainViewResolvers: ResolversWithModels<{
    MainView: MainView;
}> = {
    MainView: {
        user: ({ user }) => user,
        title: async (mainView, {}, ctx): Promise<Text> => {
            const contest = await mainView.getContest(ctx);

            return [{ value: contest?.title ?? 'TuringArena' }];
        },
        contestView: async (mainView, {}, ctx) => {
            const contest = await mainView.getContest(ctx);
            if (contest === null) return null;

            return new ContestView(contest, mainView.user);
        },
    },
};
