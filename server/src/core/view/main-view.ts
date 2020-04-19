import { gql } from 'apollo-server-core';
import { Resolvers } from '../../main/resolver-types';
import { Contest, ContestApi } from '../contest';
import { SubmissionApi } from '../submission';
import { User } from '../user';

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
    constructor(readonly contest: Contest, readonly user: User | null) {}
}

export interface MainViewModelRecord {
    MainView: MainView;
}

export const mainViewResolvers: Resolvers = {
    MainView: {
        user: ({ user }) => user,
        title: async (v, {}, ctx) => [
            { value: (await ctx.api(ContestApi).getMetadata(v.contest)).title ?? 'TuringArena' },
        ],
        contestView: ({ contest, user }) => ({ __typename: 'ContestView', contest, user }),
        pendingSubmissions: async (v, {}, ctx) =>
            v.user !== null
                ? ctx.api(SubmissionApi).pendingByContestAndUser.load({
                      contestId: v.contest.id,
                      username: v.user.username,
                  })
                : [],
    },
};
