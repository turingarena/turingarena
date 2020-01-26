import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestAwardAssignment } from './contest-award-assignment';
import { ContestAwardAssignmentView } from './contest-award-assignment-view';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemUserTackling } from './contest-problem-user-tackling';
import { ContestView } from './contest-view';
import { User } from './user';

export const contestProblemAssignmentViewSchema = gql`
    """
    Refers to a given problem, assigned in a given contest, as seen by a given user or anonymously.
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

        "Current score seen by the user for this problem in this contest."
        totalScoreVariable: ScoreVariable!

        "Awards of this problem assigned in same contest as seen by same user (or anonymously)"
        awardAssignmentViews: [ContestAwardAssignmentView!]!
    }
`;

export class ContestProblemAssignmentView {
    constructor(readonly assignment: ContestProblemAssignment, readonly user: User | null) {}

    tackling = this.user !== null ? new ContestProblemUserTackling(this.assignment, this.user) : null;

    async getTotalScoreVariable() {
        const problem = await this.assignment.getProblem();
        const { scoreDomain: domain } = await problem.getMaterial();

        return domain.variable((await this.tackling?.getScore()) ?? null);
    }
}

export const contestProblemAssignmentViewResolvers: ResolversWithModels<{
    ContestProblemAssignmentView: ContestProblemAssignmentView;
}> = {
    ContestProblemAssignmentView: {
        assignment: ({ assignment }) => assignment,
        user: ({ user }) => user,
        problemSetView: async ({ assignment, user }) => new ContestView(await assignment.getContest(), user),
        tackling: async ({ assignment, user }) =>
            user !== null ? new ContestProblemUserTackling(assignment, user) : null,
        totalScoreVariable: async view => view.getTotalScoreVariable(),
        awardAssignmentViews: async ({ assignment, user }) => {
            const problem = await assignment.getProblem();
            const material = await problem.getMaterial();

            return material.awards.map(
                award => new ContestAwardAssignmentView(new ContestAwardAssignment(assignment, award), user),
            );
        },
    },
};
