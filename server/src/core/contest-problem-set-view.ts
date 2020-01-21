import { gql } from 'apollo-server-core';
import { GradingState } from '../generated/graphql-types';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemSetItemView } from './contest-problem-set-item-view';
import { ContestView } from './contest-view';

export const contestProblemSetViewSchema = gql`
    type ContestProblemSetView {
        problemSet: ContestProblemSet!
        user: User
        contestView: ContestView!
        itemViews: [ContestProblemSetItemView!]!

        gradingState: GradingState!
    }
`;

export const contestProblemSetViewResolvers: ResolversWithModels<{
    ContestProblemSetView: ContestView;
}> = {
    ContestProblemSetView: {
        problemSet: ({ contest }) => contest,
        user: ({ user }) => user,
        contestView: contestView => contestView,
        itemViews: async ({ contest, user }) =>
            (await contest.getProblemSetItems()).map(item => new ContestProblemSetItemView(item, user)),
        gradingState: async ({ contest, user }): Promise<GradingState> => ({
            // TODO
            __typename: 'NumericGradingState',
            domain: {
                __typename: 'NumericGradeDomain',
                max: 300,
                allowPartial: true,
                decimalPrecision: 1,
            },
        }),
    },
};
