import { gql } from 'apollo-server-core';
import { ApiObject } from '../main/api';
import { Resolvers } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestView } from './contest-view';
import { SubmissionApi } from './submission';
import { User } from './user';

export const mainViewSchema = gql`
    """
    Data visible in a front page, i.e., to contestants, as seen by a given user or anonymously.
    """
    type MainView {
        "The given user, if any, or null if anonymous."
        user: User

        "The title of the page."
        title: Text!

        "The contest to show by default, or null if there is no default contest."
        contestView: ContestView

        """
        Relevant submissions that are currently pending.
        Used to poll data for such submissions more frequently, when the list is non-empty.
        """
        pendingSubmissions: [Submission!]!
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
        pendingSubmissions: async (v, {}, ctx) =>
            v.user !== null ? ctx.api(SubmissionApi).pendingByUser.load(v.user.id) : [],
    },
};
