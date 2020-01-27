import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../main/resolver-types';
import { ContestAwardAssignment } from './contest-award-assignment';
import { ContestAwardAssignmentView } from './contest-award-assignment-view';
import { ContestProblemAssignment } from './contest-problem-assignment';
import { ContestProblemAssignmentUserTackling } from './contest-problem-assignment-user-tackling';
import { ContestView } from './contest-view';
import { User } from './user';
import { ScoreField } from './feedback/score';

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
        tackling: ContestProblemAssignmentUserTackling

        "Current score seen by the user for this problem in this contest."
        totalScoreField: ScoreField!

        "Awards of this problem assigned in same contest as seen by same user (or anonymously)"
        awardAssignmentViews: [ContestAwardAssignmentView!]!
    }
`;

export class ContestProblemAssignmentView {
    constructor(readonly assignment: ContestProblemAssignment, readonly user: User | null) {}

    tackling = this.user !== null ? new ContestProblemAssignmentUserTackling(this.assignment, this.user) : null;

    async getTotalScoreField() {
        const problem = await this.assignment.getProblem();
        const { scoreRange } = await problem.getMaterial();

        return new ScoreField(scoreRange, (await this.tackling?.getScoreGrade())?.score ?? null);
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
            user !== null ? new ContestProblemAssignmentUserTackling(assignment, user) : null,
        totalScoreField: async view => view.getTotalScoreField(),
        awardAssignmentViews: async ({ assignment, user }) => {
            const problem = await assignment.getProblem();
            const material = await problem.getMaterial();

            return material.awards.map(
                award => new ContestAwardAssignmentView(new ContestAwardAssignment(assignment, award), user),
            );
        },
    },
};
