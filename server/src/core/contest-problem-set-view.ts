import { gql } from 'apollo-server-core';
import { GradeVariable } from '../generated/graphql-types';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { ContestView } from './contest-view';

export const contestProblemSetViewSchema = gql`
    type ContestProblemSetView {
        problemSet: ContestProblemSet!
        user: User
        contestView: ContestView!
        assignmentViews: [ContestProblemAssignmentView!]!

        gradeVariable: GradeVariable!
    }
`;

export const contestProblemSetViewResolvers: ResolversWithModels<{
    ContestProblemSetView: ContestView;
}> = {
    ContestProblemSetView: {
        problemSet: ({ contest }) => contest,
        user: ({ user }) => user,
        contestView: contestView => contestView,
        assignmentViews: async ({ contest, user }) =>
            (await contest.getProblemAssignments()).map(item => new ContestProblemAssignmentView(item, user)),
        gradeVariable: async ({ contest, user }): Promise<GradeVariable> => ({
            // TODO
            __typename: 'ScoreVariable',
            domain: {
                __typename: 'NumericGradeDomain',
                max: 300,
                allowPartial: true,
                decimalDigits: 1,
            },
        }),
    },
};
