import { gql } from 'apollo-server-core';
import { Resolvers } from '../../main/resolver-types';
import { typed } from '../../util/types';
import { Contest, ContestApi } from '../contest';
import { User } from '../user';
import { ContestProblemSetView } from './contest-problem-set-view';

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

export interface ContestView {
    __typename: 'ContestView';
    contest: Contest;
    user: User | null;
}

export interface ContestViewModelRecord {
    ContestView: ContestView;
}

export const contestViewResolvers: Resolvers = {
    ContestView: {
        contest: ({ contest }) => contest,
        user: ({ user }) => user,
        problemSetView: async ({ contest, user }, {}, ctx) => {
            const status = await ctx.api(ContestApi).getStatus(contest);
            switch (status) {
                case 'RUNNING':
                case 'ENDED':
                    return typed<ContestProblemSetView>({
                        __typename: 'ContestProblemSetView',
                        problemSet: { __typename: 'ContestProblemSet', contest },
                        user,
                    });
                case 'NOT_STARTED':
                default:
                    return null;
            }
        },
    },
};
