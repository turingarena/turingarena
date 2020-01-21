import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestAwardSetItem } from './contest-award-set-item';
import { ContestProblemSetItemView } from './contest-problem-set-item-view';
import { User } from './user';

export const contestAwardSetItemViewSchema = gql`
    type ContestAwardSetItemView {
        item: ContestAwardSetItem!
        user: User
        problemSetItemView: ContestProblemSetItemView!

        gradingState: GradingState!
    }
`;

export class ContestAwardSetItemView {
    constructor(readonly item: ContestAwardSetItem, readonly user: User | null) {}
}

export const contestAwardSetItemViewResolvers: ResolversWithModels<{
    ContestAwardSetItemView: ContestAwardSetItemView;
}> = {
    ContestAwardSetItemView: {
        item: ({ item }) => item,
        user: ({ user }) => user,
        problemSetItemView: async ({ item, user }) => new ContestProblemSetItemView(item.problemSetItem, user),

        gradingState: async ({ item, user }) => ({
            // TODO
            __typename: 'NumericGradingState',
            domain: {
                __typename: 'NumericGradeDomain',
                max: 30,
                allowPartial: true,
                decimalPrecision: 1,
            },
        }),
    },
};
