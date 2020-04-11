import { gql } from 'apollo-server-core';
import { ApiObject } from '../main/api';
import { Resolvers } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestView } from './contest-view';
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
}

export interface MainViewModelRecord {
    MainView: MainView;
}

export class MainViewApi extends ApiObject {
    async getContest() {
        return this.ctx.table(Contest).findOne({ where: { name: 'default' } });
    }
}

export const mainViewResolvers: Resolvers = {
    MainView: {
        user: ({ user }) => user,
        title: async (v, {}, ctx) => {
            const contest = await ctx.api(MainViewApi).getContest();

            return [{ value: contest?.title ?? 'TuringArena' }];
        },
        contestView: async (v, {}, ctx) => {
            const contest = await ctx.api(MainViewApi).getContest();
            if (contest === null) return null;

            return new ContestView(contest, v.user);
        },
    },
};
