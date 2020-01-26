import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { ContestView } from './contest-view';
import { ScoreVariable } from './feedback/score';

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
            (await contest.getProblemAssignments()).map(a => new ContestProblemAssignmentView(a, user)),
        gradeVariable: async ({ contest, user }) => {
            const assignments = await contest.getProblemAssignments();
            const variables = await Promise.all(
                assignments.map(async a => new ContestProblemAssignmentView(a, user).getScoreVariable()),
            );

            console.log(variables);

            return ScoreVariable.total(variables);
        },
    },
};
