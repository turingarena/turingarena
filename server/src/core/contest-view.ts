import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Contest } from './contest';
import { User } from './user';

export const contestViewSchema = gql`
    type ContestView {
        contest: Contest!
        user: User

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
