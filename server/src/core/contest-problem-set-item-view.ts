import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemSetItem } from './contest-problem-set-item';
import { ContestView } from './contest-view';
import { User } from './user';

export const contestProblemSetItemViewSchema = gql`
    type ContestProblemSetItemView {
        problemSetItem: ContestProblemSetItem!
        user: User
        problemSetView: ContestProblemSetView!
    }
`;

export class ContestProblemSetItemView {
    constructor(readonly item: ContestProblemSetItem, readonly user: User | null) {}
}

export const contestProblemSetItemViewResolvers: ResolversWithModels<{
    ContestProblemSetItemView: ContestProblemSetItemView;
}> = {
    ContestProblemSetItemView: {
        problemSetItem: ({ item }) => item,
        user: ({ user }) => user,
        problemSetView: async ({ item, user }) => new ContestView(await item.getContest(), user),
    },
};
