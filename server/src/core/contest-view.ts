import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestProblemSetUserTackling } from './contest-problem-set-user-tackling';
import { User } from './user';

export const contestViewSchema = gql`
    """
    A given contest, as seen by a given user or anonymously.
    """
    type ContestView {
        "The given contest."
        contest: Contest!
        "The given user."
        user: User

        "The problem-set of the given contest, as seen by the same user, if it is currently visible, and null otherwise."
        problemSetView: ContestProblemSetView
    }
`;

export class ContestView {
    constructor(readonly contest: Contest, readonly user: User | null) {}

    readonly tackling = this.user !== null ? new ContestProblemSetUserTackling(this.contest, this.user) : null;

    async getTotalScoreVariable() {
        return (await this.contest.getScoreDomain()).variable((await this.tackling?.getScore()) ?? null);
    }
}

export const contestViewResolvers: ResolversWithModels<{
    ContestView: ContestView;
}> = {
    ContestView: {
        contest: ({ contest }) => contest,
        user: ({ user }) => user,
        problemSetView: contestView => {
            switch (contestView.contest.getStatus()) {
                case 'RUNNING':
                case 'ENDED':
                    return contestView;
                case 'NOT_STARTED':
                default:
                    return null;
            }
        },
    },
};
