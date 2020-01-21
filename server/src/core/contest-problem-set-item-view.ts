import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { Award } from './award';
import { ContestAwardSetItem } from './contest-award-set-item';
import { ContestAwardSetItemView } from './contest-award-set-item-view';
import { ContestProblemSetItem } from './contest-problem-set-item';
import { ContestView } from './contest-view';
import { getProblemMetadata } from './problem-util';
import { User } from './user';

export const contestProblemSetItemViewSchema = gql`
    type ContestProblemSetItemView {
        item: ContestProblemSetItem!
        user: User
        problemSetView: ContestProblemSetView!

        gradingState: GradingState!
        canSubmit: Boolean!
        submissions: [Submission!]!

        awardSetItemViews: [ContestAwardSetItemView!]!
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
        canSubmit: () => true, // TODO
        submissions: () => [], // TODO
        awardSetItemViews: async ({ item, user }, {}, ctx) => {
            const problem = await item.getProblem();

            // FIXME: duplicated code
            const {
                scoring: { subtasks },
            } = await getProblemMetadata(ctx, problem);

            return subtasks.map(
                (subtask, index) =>
                    new ContestAwardSetItemView(new ContestAwardSetItem(item, new Award(problem, index)), user),
            );
        },
    },
};
