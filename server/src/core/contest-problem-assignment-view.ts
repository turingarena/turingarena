import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestAwardAssignment } from './contest-award-assignment';
import { ContestAwardAssignmentView } from './contest-award-assignment-view';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestView } from './contest-view';
import { User } from './user';

export const contestProblemAssignmentViewSchema = gql`
    """
    Refers to a given problem assigned in a given contest as seen by a given user or anonymously.
    """
    type ContestProblemAssignmentView {
        "Same problem assigned in same contest"
        assignment: ContestProblemAssignment!
        "Viewing user, or null if anonymous"
        user: User

        "Set of problems in same contest, as seen by same user"
        problemSetView: ContestProblemSetView!

        """
        Same problem assigned in same contest tackled by same user,
        if the user is non-anonymous and allowed to have submissions for this problem in this contest,
        and null otherwise.
        """
        tackling: ContestProblemUserTackling

        "Current grading seen by the user for this problem in this contest."
        gradingState: GradingState!

        "Awards of this problem assigned in same contest as seen by same user (or anonymously)"
        awardAssignmentViews: [ContestAwardAssignmentView!]!
    }

    """
    Refers to a given problem assigned in a given contest tackled by a given user.
    Tackling means having a collection of submissions, and possibly submit a new one.
    This is separate from ContestProblemAssignmentView since a ContestProblemUserTackling
    is available only for non-anonymous users who are allowed to have submissions (e.g., only after the contest is started).
    """
    type ContestProblemUserTackling {
        "Same problem assigned in same contest as seen by same user"
        assignmentView: ContestProblemAssignmentView!

        "User tackling the problem"
        user: User!

        "List of submissions for this problem in this contest from this user"
        submissions: [Submission!]!

        "Whether new submissions (see 'submissions') are accepted at the moment"
        canSubmit: Boolean!
    }
`;

export class ContestProblemAssignmentView {
    constructor(readonly assignment: ContestProblemAssignment, readonly user: User | null) {}
}

export class ContestProblemUserTackling {
    constructor(readonly assignment: ContestProblemAssignment, readonly user: User) {}
}

export const contestProblemAssignmentViewResolvers: ResolversWithModels<{
    ContestProblemAssignmentView: ContestProblemAssignmentView;
    ContestProblemUserTackling: ContestProblemUserTackling;
}> = {
    ContestProblemAssignmentView: {
        assignment: ({ assignment }) => assignment,
        user: ({ user }) => user,
        problemSetView: async ({ assignment, user }) => new ContestView(await assignment.getContest(), user),
        tackling: async ({ assignment, user }) =>
            user !== null ? new ContestProblemUserTackling(assignment, user) : null,
        gradingState: async ({ assignment, user }) => ({
            // TODO
            __typename: 'NumericGradingState',
            domain: {
                __typename: 'NumericGradeDomain',
                max: 100,
                allowPartial: true,
                decimalPrecision: 1,
            },
        }),
        awardAssignmentViews: async ({ assignment, user }) => {
            const problem = await assignment.getProblem();
            const material = await problem.getMaterial();

            return material.awards.map(
                award => new ContestAwardAssignmentView(new ContestAwardAssignment(assignment, award), user),
            );
        },
    },
    ContestProblemUserTackling: {
        canSubmit: () => true, // TODO
        submissions: () => [], // TODO
        assignmentView: ({ assignment, user }) => new ContestProblemAssignmentView(assignment, user),
        user: ({ user }) => user,
    },
};
