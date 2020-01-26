import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestAwardAssignment } from './contest-award-assignment';
import { ContestProblemAssignmentView } from './contest-problem-assignment-view';
import { User } from './user';

export const contestAwardAssignmentViewSchema = gql`
    type ContestAwardAssignmentView {
        assignment: ContestAwardAssignment!
        user: User
        problemAssignmentView: ContestProblemAssignmentView!

        gradeVariable: GradeVariable!
    }
`;

export class ContestAwardAssignmentView {
    constructor(readonly assignment: ContestAwardAssignment, readonly user: User | null) {}
}

export const contestAwardAssignmentViewResolvers: ResolversWithModels<{
    ContestAwardAssignmentView: ContestAwardAssignmentView;
}> = {
    ContestAwardAssignmentView: {
        assignment: ({ assignment }) => assignment,
        user: ({ user }) => user,
        problemAssignmentView: async ({ assignment, user }) =>
            new ContestProblemAssignmentView(assignment.problemAssignment, user),

        gradeVariable: async ({ assignment, user }) => ({
            // TODO
            __typename: 'ScoreVariable',
            domain: {
                __typename: 'NumericGradeDomain',
                max: 30,
                allowPartial: true,
                decimalDigits: 1,
            },
        }),
    },
};
