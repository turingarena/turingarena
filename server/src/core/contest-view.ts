import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { ContestProblemSet } from './contest-problem-set';
import { ContestProblemSetView } from './contest-problem-set-view';
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
}

export const contestViewResolvers: ResolversWithModels<{
    ContestView: ContestView;
}> = {
    ContestView: {
        contest: ({ contest }) => contest,
        user: ({ user }) => user,
        problemSetView: ({ contest, user }) => {
            switch (contest.getStatus()) {
                case 'RUNNING':
                case 'ENDED':
                    return new ContestProblemSetView(new ContestProblemSet(contest), user);
                case 'NOT_STARTED':
                default:
                    return null;
            }
        },
    },
};
