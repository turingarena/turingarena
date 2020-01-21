import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemSetItem } from './contest-problem-set-item';
import { ContestView } from './contest-view';
import { User } from './user';

export const contestProblemSetItemViewSchema = gql`
    type ContestProblemSetItemView {
        item: ContestProblemSetItem!
        user: User
        problemSetView: ContestProblemSetView!
        gradingState: GradingState!
    }
`;

export class ContestProblemSetItemView {
    constructor(readonly item: ContestProblemSetItem, readonly user: User | null) {}
}

export const contestProblemSetItemViewResolvers: ResolversWithModels<{
    ContestProblemSetItemView: ContestProblemSetItemView;
}> = {
    ContestProblemSetItemView: {
        item: ({ item }) => item,
        user: ({ user }) => user,
        problemSetView: async ({ item, user }) => new ContestView(await item.getContest(), user),
        gradingState: async ({ item, user }) => ({
            // TODO
            __typename: 'NumericGradingState',
            domain: {
                __typename: 'NumericGradeDomain',
                max: 100,
                allowPartial: true,
                decimalPrecision: 1,
            },
        }),
    },
};
